---
title: AVSession 业务流错误索引
purpose: /diag wiki-reader 索引式检索——日志报错事件名 -> 直达 file:line + 所在业务流页
source_repo: multimedia_av_session
domain: AV_SESSION
crg_commit: a4ec47de96f7
last_updated: 2026-07-24
---

# 错误索引 (error_index)

> 日志里出现某 HiSysEvent 事件名（如 `CONTROL_COMMAND_FAILED`）→ 在下表查事件名 → 拿到 `file:line`（上报点）+ 所在业务流页链接 → 一键跳到调用链上下文。
>
> 收录所有与错误诊断相关的 HiSysEvent 上报点：FAULT / SECURITY 级报错、带 ERROR_CODE 的 API 行为事件，以及与错误诊断强相关的 BEHAVIOR / STATISTIC 埋点（焦点丢失、命令失败率、会话生命周期统计、服务启动路径等）。纯行为埋点的完整字段定义见仓内 `hisysevent.yaml`（domain `AV_SESSION`）。

## 如何用

1. /diag 拿到日志 → log-triage digest 里标出 claimed error 的事件名（如 `CONTROL_PERMISSION_DENIED`）。
2. 本索引按事件名查表 → 得到上报 `file:line` + 触发流 + 所在业务流页。
3. 点业务流页看 mermaid 调用链 + 逐步错误上报，定位近一步到位。

## 错误事件目录

共收录 **49** 条去重错误上报点，覆盖 **13** 个事件，分布在 **8** 个业务流页。

### `AVSESSION_WRONG_STATE`

| 上报 file:line | 类型 | 级别 | 触发流 | 错误条件 | 所在业务流页 |
|---|---|---|---|---|---|
| `services/session/server/avsession_service.cpp:1384` | FAULT | MINOR | 会话状态校验 PlayStateCheck | renderer RUNNING 但 session 非 PLAYING / renderer PAUSED 或 STOPPED 但 session 仍 PLAYING | [avsession-lifecycle.md](avsession-lifecycle.md), [event-callback-lifecycle.md](event-callback-lifecycle.md) |

### `CONTROL_COMMAND_FAILED`

| 上报 file:line | 类型 | 级别 | 触发流 | 错误条件 | 所在业务流页 |
|---|---|---|---|---|---|
| `frameworks/js/napi/session/src/napi_avsession_manager.cpp:1366` | FAULT | MINOR | SendSystemControlCommand | native 投递失败 SEND_CMD_FAILED | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `frameworks/native/session/src/avsession_manager_impl.cpp:439` | FAULT | MINOR | SendSystemControlCommand | command.IsValid 为假 INVALID_COMMAND | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `frameworks/native/session/src/avsession_manager_impl.cpp:446` | FAULT | MINOR | SendSystemControlCommand | GetService 返回 nullptr GET_SERVICE_ERROR | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `frameworks/taihe/src/taihe_avsession_manager.cpp:1276` | FAULT | MINOR | SendSystemControlCommand | native 投递失败 SEND_CMD_FAILED | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `services/session/ipc/stub/avsession_service_stub.cpp:456` | FAULT | MINOR | SendSystemControlCommand | data 读 parcel 失败 READ_PARCELABLE_FAILED | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `services/session/server/avsession_item.cpp:2998` | FAULT | MINOR | ExecuteCommonCommand | 命令码非法 INVALID_COMMAND | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `services/session/server/avsession_service.cpp:1883` | FAULT | MINOR | Close->CreateSessionInner | CreateNewSession 返回 null,内存分配失败 | [avsession-lifecycle.md](avsession-lifecycle.md), [command-control-lifecycle.md](command-control-lifecycle.md) |
| `services/session/server/avsession_service.cpp:3341` | FAULT | MINOR | RegisterClientDeathObserver | new ClientDeathRecipient 失败(nullptr,内存分配失败) | [client-listener-lifecycle.md](client-listener-lifecycle.md), [command-control-lifecycle.md](command-control-lifecycle.md) |
| `services/session/server/avsession_service.cpp:3348` | FAULT | MINOR | RegisterClientDeathObserver | AddDeathRecipient 失败(注册死亡回调失败) | [client-listener-lifecycle.md](client-listener-lifecycle.md), [command-control-lifecycle.md](command-control-lifecycle.md) |

### `CONTROL_COMMAND_FAILED_RATE`

| 上报 file:line | 类型 | 级别 | 触发流 | 错误条件 | 所在业务流页 |
|---|---|---|---|---|---|
| `utils/src/avsession_sysevent.cpp:123` | STATISTIC | MINOR | SendSystemControlCommand | 周期聚合命令失败率 | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `utils/src/avsession_sysevent.cpp:126` | STATISTIC | MINOR | SendSystemControlCommand | succCount>allCount 异常记 0 | [command-control-lifecycle.md](command-control-lifecycle.md) |

### `CONTROL_PERMISSION_DENIED`

| 上报 file:line | 类型 | 级别 | 触发流 | 错误条件 | 所在业务流页 |
|---|---|---|---|---|---|
| `frameworks/js/napi/session/src/napi_avsession_manager.cpp:1375` | SECURITY | CRITICAL | SendSystemControlCommand | ERR_NO_PERMISSION native 无权限 | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `frameworks/taihe/src/taihe_avsession_manager.cpp:1289` | SECURITY | CRITICAL | SendSystemControlCommand | ERR_NO_PERMISSION | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `services/session/ipc/stub/avsession_service_stub.cpp:112` | SECURITY | CRITICAL | SendSystemControlCommand | IPC stub 系统权限校验失败 | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `services/session/ipc/stub/avsession_service_stub.cpp:267` | SECURITY | CRITICAL | SendSystemControlCommand | IPC stub 系统权限校验失败 | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `services/session/ipc/stub/avsession_service_stub.cpp:515` | SECURITY | CRITICAL | SendSystemControlCommand | IPC stub 系统权限校验失败 | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `services/session/ipc/stub/avsession_service_stub.cpp:645` | SECURITY | CRITICAL | SendSystemControlCommand | IPC stub 系统权限校验失败 | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `services/session/ipc/stub/avsession_service_stub.cpp:786` | SECURITY | CRITICAL | SendSystemControlCommand | IPC stub 系统权限校验失败 | [command-control-lifecycle.md](command-control-lifecycle.md) |
| `services/session/server/avsession_service.cpp:2225` | SECURITY | CRITICAL | SendSystemControlCommand | 获取描述符权限校验失败 | [command-control-lifecycle.md](command-control-lifecycle.md) |

### `FOCUS_CHANGE`

| 上报 file:line | 类型 | 级别 | 触发流 | 错误条件 | 所在业务流页 |
|---|---|---|---|---|---|
| `services/session/server/avsession_service.cpp:709` | BEHAVIOR | MINOR | OnAddSystemAbility | topSession 切换上报新旧会话信息 | [device-connect-lifecycle.md](device-connect-lifecycle.md), [event-callback-lifecycle.md](event-callback-lifecycle.md) |
| `services/session/server/avsession_service.cpp:749` | BEHAVIOR | MINOR | OnAddSystemAbility | newTopSession 为空 焦点丢失 | [device-connect-lifecycle.md](device-connect-lifecycle.md), [event-callback-lifecycle.md](event-callback-lifecycle.md) |
| `services/session/server/focus_session_strategy.cpp:175` | BEHAVIOR | MINOR | OnAddSystemAbility | 焦点策略选中焦点 session uid | [device-connect-lifecycle.md](device-connect-lifecycle.md), [event-callback-lifecycle.md](event-callback-lifecycle.md) |

### `PLAYING_AVSESSION_STATS`

| 上报 file:line | 类型 | 级别 | 触发流 | 错误条件 | 所在业务流页 |
|---|---|---|---|---|---|
| `utils/src/avsession_storage_event.cpp:364` | STATISTIC | CRITICAL | OnReceiveEvent | 存储 bundle 数超限立即上报/周期上报;本域无 FAULT/SECURITY 级,仅 STATISTIC 级埋点 | [event-callback-lifecycle.md](event-callback-lifecycle.md), [serialization-lifecycle.md](serialization-lifecycle.md) |
| `utils/src/avsession_sysevent.cpp:200` | STATISTIC | CRITICAL | OnReceiveEvent | 周期聚合播放会话质量统计 | [event-callback-lifecycle.md](event-callback-lifecycle.md) |
| `utils/src/avsession_sysevent.cpp:451` | STATISTIC | CRITICAL | OnReceiveEvent | 单会话播放质量上报 | [event-callback-lifecycle.md](event-callback-lifecycle.md) |

### `PLAYING_COMBIND_AVSESSION_STATIS`

| 上报 file:line | 类型 | 级别 | 触发流 | 错误条件 | 所在业务流页 |
|---|---|---|---|---|---|
| `utils/src/avsession_sysevent.cpp:70` | STATISTIC | MINOR | OnReceiveEvent | 低质量播放统计 | [event-callback-lifecycle.md](event-callback-lifecycle.md) |

### `REMOTE_CONTROL_FAILED`

| 上报 file:line | 类型 | 级别 | 触发流 | 错误条件 | 所在业务流页 |
|---|---|---|---|---|---|
| `services/session/server/hw_cast_stream_player.cpp:169` | FAULT | MINOR | GetAVCastControllerInner | 非法控制命令 INNER_ERROR | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/hw_cast_stream_player.cpp:82` | FAULT | MINOR | GetAVCastControllerInner | streamPlayer_ 为空 INNER_ERROR | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/remote/remote_session_sink_impl.cpp:154` | FAULT | MINOR | CastAudioFromRemote | PutControlCommand 返回非成功 TIME_OUT | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/remote/remote_session_sink_impl.cpp:172` | FAULT | MINOR | CastAudioFromRemote | PutCommonCommand 返回非成功 TIME_OUT | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/remote/remote_session_sink_impl.cpp:60` | FAULT | MINOR | CastAudioFromRemote | sink 侧远端断开 REMOTE_DISCONNECTED | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/remote/remote_session_source_impl.cpp:152` | FAULT | MINOR | CastAudioToRemote | PutAVMetaData 返回非成功 TIME_OUT | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/remote/remote_session_source_impl.cpp:179` | FAULT | MINOR | CastAudioToRemote | PutAVPlaybackState 返回非成功 TIME_OUT | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/remote/remote_session_source_impl.cpp:204` | FAULT | MINOR | CastAudioToRemote | PutExtras 返回非成功 TIME_OUT | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/remote/remote_session_source_impl.cpp:228` | FAULT | MINOR | CastAudioToRemote | PutAVQueueImage 返回非成功 TIME_OUT | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/remote/remote_session_source_impl.cpp:252` | FAULT | MINOR | CastAudioToRemote | PutAVQueueTitle 返回非成功 TIME_OUT | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/remote/remote_session_source_impl.cpp:276` | FAULT | MINOR | CastAudioToRemote | PutCommonCommand 返回非成功 TIME_OUT | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/remote/remote_session_source_impl.cpp:64` | FAULT | MINOR | CastAudioToRemote | 远端设备断开 REMOTE_DISCONNECTED | [cast-lifecycle.md](cast-lifecycle.md) |

### `SESSION_API_BEHAVIOR`

| 上报 file:line | 类型 | 级别 | 触发流 | 错误条件 | 所在业务流页 |
|---|---|---|---|---|---|
| `services/session/server/avsession_item.cpp:1264` | BEHAVIOR | CRITICAL | GetAVCastControllerInner | 投屏控制器信息上报 | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/avsession_item.cpp:1273` | BEHAVIOR | CRITICAL | GetAVCastControllerInner | 远端播放器错误回调 | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/avsession_item.cpp:179` | BEHAVIOR | CRITICAL | DestroyTask->Destroy | 上报 Destroy API 行为,ERROR_CODE=AVSESSION_SUCCESS | [avsession-lifecycle.md](avsession-lifecycle.md) |
| `services/session/server/avsession_service.cpp:1952` | BEHAVIOR | CRITICAL | Close->CreateSessionInner | ReportSessionInfo 上报 CreateSession 结果,ERROR_CODE=res | [avsession-lifecycle.md](avsession-lifecycle.md) |

### `SESSION_CAST`

| 上报 file:line | 类型 | 级别 | 触发流 | 错误条件 | 所在业务流页 |
|---|---|---|---|---|---|
| `services/session/server/avsession_service.cpp:3957` | BEHAVIOR | MINOR | CastAudioForAll | CastAudioToRemote 成功后投屏行为埋点 | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/avsession_service_ext.cpp:402` | BEHAVIOR | MINOR | CastAudioFromRemote | 远端 cast 会话创建回调埋点 | [cast-lifecycle.md](cast-lifecycle.md) |
| `services/session/server/avsession_service_ext.cpp:602` | BEHAVIOR | MINOR | CastAudioForAll | StartCast 建立成功后投屏行为埋点 | [cast-lifecycle.md](cast-lifecycle.md) |

### `SESSION_CAST_CONTROL`

| 上报 file:line | 类型 | 级别 | 触发流 | 错误条件 | 所在业务流页 |
|---|---|---|---|---|---|
| `utils/src/avsession_sysevent.cpp:398` | BEHAVIOR | CRITICAL | RegisterListenerStreamToCast | 投屏控制时延埋点 断连时上报 | [cast-lifecycle.md](cast-lifecycle.md) |

### `SESSION_LIFECYCLE_STATISTICS`

| 上报 file:line | 类型 | 级别 | 触发流 | 错误条件 | 所在业务流页 |
|---|---|---|---|---|---|
| `utils/src/avsession_sysevent.cpp:101` | STATISTIC | MINOR | Close->HandleSessionRelease/ReportSessionState | 会话生命周期 create/release 统计(行为埋点) | [avsession-lifecycle.md](avsession-lifecycle.md) |

### `SESSION_SERVICE_START`

| 上报 file:line | 类型 | 级别 | 触发流 | 错误条件 | 所在业务流页 |
|---|---|---|---|---|---|
| `services/session/server/avsession_service.cpp:203` | BEHAVIOR | MINOR | OnStart | 服务启动成功路径埋点 启动失败则不达 | [device-connect-lifecycle.md](device-connect-lifecycle.md) |

## 无 FAULT/SECURITY 上报的业务域

下列业务域 grep 不到 FAULT/SECURITY 级 HiSysEvent 上报，日志若指向这些域，错误多以 hilog（SLOGE）或返回码形式间接触发：

| 业务流页 | 说明 |
|---|---|
| [client-listener-lifecycle.md](client-listener-lifecycle.md) | 本域 InitListener/ProcFromNext 链无 FAULT/SECURITY 级 HiSysEvent,仅 hilog E |
| [ui-frontend-lifecycle.md](ui-frontend-lifecycle.md) | 本域无 FAULT/SECURITY 级 HiSysEvent 上报(纯前端 JS 本地逻辑) |
