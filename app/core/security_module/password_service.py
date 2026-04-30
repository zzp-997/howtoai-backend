"""
密码安全服务
密码强度校验、密码过期检测、历史密码检查
"""
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import logging
from app.core.config import settings
from app.extensions import db

logger = logging.getLogger(__name__)


class PasswordService:
    """密码安全服务"""

    # 密码强度等级
    STRENGTH_WEAK = "weak"
    STRENGTH_MEDIUM = "medium"
    STRENGTH_STRONG = "strong"
    STRENGTH_VERY_STRONG = "very_strong"

    # 密码复杂度规则
    PATTERNS = {
        "uppercase": r"[A-Z]",
        "lowercase": r"[a-z]",
        "digit": r"\d",
        "special": r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]"
    }

    # 常见弱密码列表
    COMMON_PASSWORDS = {
        "password", "123456", "12345678", "qwerty", "abc123",
        "monkey", "master", "dragon", "111111", "baseball",
        "iloveyou", "trustno1", "sunshine", "princess", "admin",
        "welcome", "shadow", "ashley", "football", "jesus",
        "michael", "ninja", "mustang", "password1", "password123"
    }

    @classmethod
    def validate_password(cls, password: str, user_info: Optional[Dict] = None) -> Dict:
        """
        验证密码强度

        Args:
            password: 密码
            user_info: 用户信息（用于检查密码是否包含个人信息）

        Returns:
            验证结果，包含是否通过、强度等级、错误信息
        """
        errors = []
        warnings = []
        checks = {}

        # 1. 长度检查
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            errors.append(f"密码长度至少需要 {settings.PASSWORD_MIN_LENGTH} 位")
        checks["length"] = len(password) >= settings.PASSWORD_MIN_LENGTH

        # 2. 复杂度检查
        complexity_count = 0

        if settings.PASSWORD_REQUIRE_UPPERCASE:
            has_upper = bool(re.search(cls.PATTERNS["uppercase"], password))
            checks["uppercase"] = has_upper
            if not has_upper:
                errors.append("密码需要包含大写字母")
            else:
                complexity_count += 1
        else:
            checks["uppercase"] = True

        if settings.PASSWORD_REQUIRE_LOWERCASE:
            has_lower = bool(re.search(cls.PATTERNS["lowercase"], password))
            checks["lowercase"] = has_lower
            if not has_lower:
                errors.append("密码需要包含小写字母")
            else:
                complexity_count += 1
        else:
            checks["lowercase"] = True

        if settings.PASSWORD_REQUIRE_DIGIT:
            has_digit = bool(re.search(cls.PATTERNS["digit"], password))
            checks["digit"] = has_digit
            if not has_digit:
                errors.append("密码需要包含数字")
            else:
                complexity_count += 1
        else:
            checks["digit"] = True

        if settings.PASSWORD_REQUIRE_SPECIAL:
            has_special = bool(re.search(cls.PATTERNS["special"], password))
            checks["special"] = has_special
            if not has_special:
                errors.append("密码需要包含特殊字符")
            else:
                complexity_count += 1
        else:
            checks["special"] = True

        # 3. 弱密码检查
        if password.lower() in cls.COMMON_PASSWORDS:
            errors.append("密码过于简单，请使用更复杂的密码")
            checks["not_common"] = False
        else:
            checks["not_common"] = True

        # 4. 用户信息检查
        if user_info:
            username = user_info.get("username", "").lower()
            email = user_info.get("email", "").lower()
            phone = user_info.get("phone", "")

            if username and username in password.lower():
                warnings.append("密码不应包含用户名")
                checks["no_username"] = False
            else:
                checks["no_username"] = True

            if email and email.split("@")[0] in password.lower():
                warnings.append("密码不应包含邮箱前缀")
                checks["no_email"] = False
            else:
                checks["no_email"] = True

            if phone and phone in password:
                warnings.append("密码不应包含手机号")
                checks["no_phone"] = False
            else:
                checks["no_phone"] = True

        # 5. 连续字符检查
        if cls._has_sequential_chars(password):
            warnings.append("密码包含连续字符（如123、abc）")
            checks["no_sequential"] = False
        else:
            checks["no_sequential"] = True

        # 6. 重复字符检查
        if cls._has_repeated_chars(password):
            warnings.append("密码包含过多重复字符")
            checks["no_repeated"] = False
        else:
            checks["no_repeated"] = True

        # 计算强度等级
        strength = cls._calculate_strength(password, complexity_count, checks)

        return {
            "valid": len(errors) == 0,
            "strength": strength,
            "errors": errors,
            "warnings": warnings,
            "checks": checks
        }

    @classmethod
    def get_password_strength(cls, password: str) -> Tuple[str, int]:
        """
        获取密码强度等级和分数

        Args:
            password: 密码

        Returns:
            (强度等级, 分数0-100)
        """
        result = cls.validate_password(password)
        score = 0

        # 基础长度分数
        length = len(password)
        if length >= 8:
            score += 20
        if length >= 12:
            score += 10
        if length >= 16:
            score += 10

        # 复杂度分数
        checks = result["checks"]
        if checks.get("uppercase"):
            score += 15
        if checks.get("lowercase"):
            score += 10
        if checks.get("digit"):
            score += 15
        if checks.get("special"):
            score += 20

        # 扣分项
        if not checks.get("not_common"):
            score -= 30
        if not checks.get("no_sequential"):
            score -= 10
        if not checks.get("no_repeated"):
            score -= 10

        # 确保分数在0-100范围内
        score = max(0, min(100, score))

        # 确定强度等级
        if score < 40:
            strength = cls.STRENGTH_WEAK
        elif score < 60:
            strength = cls.STRENGTH_MEDIUM
        elif score < 80:
            strength = cls.STRENGTH_STRONG
        else:
            strength = cls.STRENGTH_VERY_STRONG

        return strength, score

    @classmethod
    def check_password_expiry(cls, password_changed_at: Optional[datetime]) -> Dict:
        """
        检查密码是否过期或即将过期

        Args:
            password_changed_at: 密码最后修改时间

        Returns:
            过期状态信息
        """
        if password_changed_at is None:
            # 如果没有记录，视为需要修改
            return {
                "expired": True,
                "expiring_soon": True,
                "days_remaining": 0,
                "message": "请设置新密码"
            }

        now = datetime.now()
        expiry_date = password_changed_at + timedelta(days=settings.PASSWORD_EXPIRE_DAYS)
        days_remaining = (expiry_date - now).days

        if days_remaining <= 0:
            return {
                "expired": True,
                "expiring_soon": True,
                "days_remaining": 0,
                "message": "密码已过期，请修改密码"
            }
        elif days_remaining <= 7:
            return {
                "expired": False,
                "expiring_soon": True,
                "days_remaining": days_remaining,
                "message": f"密码将在 {days_remaining} 天后过期，请及时修改"
            }
        else:
            return {
                "expired": False,
                "expiring_soon": False,
                "days_remaining": days_remaining,
                "message": None
            }

    @classmethod
    def check_password_history(cls, password: str, password_history: Optional[str],
                                user_id: int) -> bool:
        """
        检查密码是否与历史密码重复

        Args:
            password: 新密码
            password_history: 历史密码JSON字符串
            user_id: 用户ID

        Returns:
            True表示密码可用，False表示与历史密码重复
        """
        if not password_history:
            return True

        try:
            history = json.loads(password_history)
        except (json.JSONDecodeError, TypeError):
            history = []

        # 计算新密码的哈希
        password_hash = cls._hash_password(password)

        # 检查是否在历史记录中
        if password_hash in history:
            logger.info(f"用户 {user_id} 尝试使用历史密码")
            return False

        return True

    @classmethod
    def update_password_history(cls, password_history: Optional[str], new_password: str) -> str:
        """
        更新密码历史记录

        Args:
            password_history: 当前历史密码JSON字符串
            new_password: 新密码

        Returns:
            更新后的历史密码JSON字符串
        """
        try:
            history = json.loads(password_history) if password_history else []
        except (json.JSONDecodeError, TypeError):
            history = []

        # 添加新密码哈希
        new_hash = cls._hash_password(new_password)
        history.append(new_hash)

        # 保留最近N条记录
        if len(history) > settings.PASSWORD_HISTORY_COUNT:
            history = history[-settings.PASSWORD_HISTORY_COUNT:]

        return json.dumps(history)

    @classmethod
    def generate_password_suggestions(cls, user_info: Optional[Dict] = None) -> List[str]:
        """
        生成密码建议

        Args:
            user_info: 用户信息

        Returns:
            密码建议列表
        """
        suggestions = [
            "使用至少8个字符",
            "混合使用大小写字母、数字和特殊字符",
            "避免使用生日、手机号等个人信息",
            "不要使用常见单词或连续数字",
            "考虑使用密码短语，如：MyDog#Loves2Bark!"
        ]

        if user_info:
            suggestions.append("密码中不要包含用户名或邮箱信息")

        return suggestions

    @staticmethod
    def _hash_password(password: str) -> str:
        """计算密码哈希（用于历史比对）"""
        return hashlib.sha256(password.encode()).hexdigest()[:32]

    @staticmethod
    def _has_sequential_chars(password: str, min_length: int = 3) -> bool:
        """检查是否包含连续字符"""
        sequences = [
            "abcdefghijklmnopqrstuvwxyz",
            "zyxwvutsrqponmlkjihgfedcba",
            "01234567890",
            "09876543210",
            "!@#$%^&*()"
        ]

        password_lower = password.lower()
        for seq in sequences:
            for i in range(len(seq) - min_length + 1):
                if seq[i:i + min_length] in password_lower:
                    return True
        return False

    @staticmethod
    def _has_repeated_chars(password: str, max_repeat: int = 3) -> bool:
        """检查是否包含过多重复字符"""
        if not password:
            return False

        count = 1
        for i in range(1, len(password)):
            if password[i] == password[i - 1]:
                count += 1
                if count > max_repeat:
                    return True
            else:
                count = 1
        return False

    @classmethod
    def _calculate_strength(cls, password: str, complexity_count: int, checks: Dict) -> str:
        """计算密码强度等级"""
        length = len(password)

        # 根据长度和复杂度综合判断
        if length < 8 or complexity_count < 2:
            return cls.STRENGTH_WEAK
        elif length < 10 or complexity_count < 3:
            return cls.STRENGTH_MEDIUM
        elif length < 14 or complexity_count < 4:
            return cls.STRENGTH_STRONG
        else:
            return cls.STRENGTH_VERY_STRONG
