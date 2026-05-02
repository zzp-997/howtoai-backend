"""
统一业务错误码定义

规则：
- 1xxxx: 通用错误
- 2xxxx: 认证/权限错误
- 3xxxx: 业务逻辑错误（按模块细分）
  - 301xx: 审批
  - 302xx: 会议室/预定
  - 303xx: 考勤
  - 304xx: 报销
  - 305xx: 文档
  - 306xx: 差旅
  - 307xx: 请假
  - 308xx: 配置
  - 309xx: 公告
  - 310xx: 待办
  - 311xx: 用户
"""
from enum import IntEnum


class ErrorCode(IntEnum):
    # ===== 通用 1xxxx =====
    SUCCESS = 200
    BAD_REQUEST = 10001           # 请求参数错误
    VALIDATION_ERROR = 10002      # 数据校验失败
    NOT_FOUND = 10003             # 资源不存在
    DUPLICATE = 10004             # 重复操作
    OPERATION_FAILED = 10005      # 操作失败（通用）

    # ===== 认证/权限 2xxxx =====
    UNAUTHORIZED = 20001          # 未登录
    TOKEN_EXPIRED = 20002         # Token 过期
    PERMISSION_DENIED = 20003     # 无权限
    ACCOUNT_DISABLED = 20004      # 账号已禁用
    LOGIN_FAILED = 20005          # 登录失败

    # ===== 业务逻辑 3xxxx =====
    # 审批 301xx
    APPROVAL_NOT_FOUND = 30101
    APPROVAL_CHAIN_NOT_FOUND = 30102
    APPROVAL_CHAIN_INVALID = 30103
    APPROVAL_STATUS_INVALID = 30104
    APPROVAL_OPERATION_FAILED = 30105

    # 会议室/预定 302xx
    ROOM_NOT_FOUND = 30201
    RESERVATION_NOT_FOUND = 30202
    RESERVATION_CONFLICT = 30203

    # 考勤 303xx
    MAKEUP_NOT_FOUND = 30301
    MAKEUP_OPERATION_FAILED = 30302

    # 报销 304xx
    EXPENSE_NOT_FOUND = 30401
    EXPENSE_STATUS_INVALID = 30402

    # 文档 305xx
    DOCUMENT_NOT_FOUND = 30501
    DOCUMENT_PERMISSION_DENIED = 30502

    # 差旅 306xx
    TRIP_NOT_FOUND = 30601
    TRIP_STATUS_INVALID = 30602

    # 请假 307xx
    LEAVE_NOT_FOUND = 30701
    LEAVE_STATUS_INVALID = 30702
    LEAVE_DATE_CONFLICT = 30703

    # 配置 308xx
    CONFIG_NOT_FOUND = 30801
    TEMPLATE_NOT_FOUND = 30802
    CITY_NOT_FOUND = 30803
    HOLIDAY_NOT_FOUND = 30804

    # 公告 309xx
    ANNOUNCEMENT_NOT_FOUND = 30901

    # 待办 310xx
    TODO_NOT_FOUND = 31001

    # 用户 311xx
    USER_NOT_FOUND = 31101


# 错误码 → 默认提示文案映射
ERROR_MESSAGES = {
    # 通用
    ErrorCode.SUCCESS: "操作成功",
    ErrorCode.BAD_REQUEST: "请求参数错误",
    ErrorCode.VALIDATION_ERROR: "数据校验失败",
    ErrorCode.NOT_FOUND: "资源不存在",
    ErrorCode.DUPLICATE: "请勿重复操作",
    ErrorCode.OPERATION_FAILED: "操作失败，请稍后重试",
    # 认证/权限
    ErrorCode.UNAUTHORIZED: "请先登录",
    ErrorCode.TOKEN_EXPIRED: "登录已过期，请重新登录",
    ErrorCode.PERMISSION_DENIED: "暂无权限",
    ErrorCode.ACCOUNT_DISABLED: "账号已禁用",
    ErrorCode.LOGIN_FAILED: "用户名或密码错误",
    # 审批
    ErrorCode.APPROVAL_NOT_FOUND: "申请不存在",
    ErrorCode.APPROVAL_CHAIN_NOT_FOUND: "审批链不存在",
    ErrorCode.APPROVAL_CHAIN_INVALID: "审批链无效",
    ErrorCode.APPROVAL_STATUS_INVALID: "审批状态不允许此操作",
    ErrorCode.APPROVAL_OPERATION_FAILED: "审批操作失败",
    # 会议室/预定
    ErrorCode.ROOM_NOT_FOUND: "会议室不存在",
    ErrorCode.RESERVATION_NOT_FOUND: "预定不存在",
    ErrorCode.RESERVATION_CONFLICT: "时间冲突",
    # 考勤
    ErrorCode.MAKEUP_NOT_FOUND: "补卡申请不存在",
    ErrorCode.MAKEUP_OPERATION_FAILED: "补卡操作失败",
    # 报销
    ErrorCode.EXPENSE_NOT_FOUND: "报销单不存在",
    ErrorCode.EXPENSE_STATUS_INVALID: "报销单状态不允许此操作",
    # 文档
    ErrorCode.DOCUMENT_NOT_FOUND: "文档不存在",
    ErrorCode.DOCUMENT_PERMISSION_DENIED: "无权限操作此文档",
    # 差旅
    ErrorCode.TRIP_NOT_FOUND: "差旅申请不存在",
    ErrorCode.TRIP_STATUS_INVALID: "差旅状态不允许此操作",
    # 请假
    ErrorCode.LEAVE_NOT_FOUND: "请假申请不存在",
    ErrorCode.LEAVE_STATUS_INVALID: "请假状态不允许此操作",
    ErrorCode.LEAVE_DATE_CONFLICT: "日期与已存在的请假申请重叠",
    # 配置
    ErrorCode.CONFIG_NOT_FOUND: "配置不存在",
    ErrorCode.TEMPLATE_NOT_FOUND: "模板不存在",
    ErrorCode.CITY_NOT_FOUND: "城市不存在",
    ErrorCode.HOLIDAY_NOT_FOUND: "节假日配置不存在",
    # 公告
    ErrorCode.ANNOUNCEMENT_NOT_FOUND: "公告不存在",
    # 待办
    ErrorCode.TODO_NOT_FOUND: "待办不存在",
    # 用户
    ErrorCode.USER_NOT_FOUND: "用户不存在",
}
