---
title: Cast 投屏生命周期
business_domain: Cast
lifecycle: 投屏发起→音频投递到远端→远端/本地双向投递→投屏控制器建立与命令同步
flows: [13:CastAudioToRemote, 5:CastAudioFromRemote, 3:CastAudioForAll, 4:GetAVCastControllerInner, 27:RegisterListenerStreamToCast]
entry_points: [CastAudioToRemote, CastAudioFromRemote, CastAudioForAll, GetAVCastControllerInner, RegisterListenerStreamToCast]
hisysevent_events: [SESSION_CAST, SESSION_CAST_CONTROL, REMOTE_CONTROL_FAILED, SESSION_API_BEHAVIOR]
crg_commit: a4ec47de96f7
last_updated: 2026-07-24
source_repo: multimedia_av_session
---

# Cast 投屏生命周期

## 概述
本生命周期覆盖 AVSession 音频投屏的端到端链路：上层 `AVSessionService::CastAudioForAll`/`StartCast` 发起投屏并写 `SESSION_CAST` 行为埋点；`AVSessionItem::CastAudioToRemote` 把本地 meta/playbackstate/queue 投递到远端 sink；`CastAudioFromRemote` 反向在远端建会话；`GetAVCastControllerInner` 建投屏控制器并初始化 cast 命令集；`RegisterListenerStreamToCast` 注册监听并启动/停止投屏。典型报错方向是远端投递超时/连接断开（`REMOTE_CONTROL_FAILED`）和投屏控制时延埋点（`SESSION_CAST_CONTROL`）。

## 调用序列

### CastAudioToRemote (flow 13)
```mermaid
flowchart LR
    f13_1["CastAudioToRemote<br/>services/session/server/avsession_item.cpp:3448"] --> f13_2["GetMetaData<br/>services/session/server/avsession_item.cpp:2727"]
    f13_2 --> f13_3["GetPlaybackState<br/>services/session/server/avsession_item.cpp:2715"]
    f13_3 --> f13_4["SetAVMetaData<br/>services/session/server/avsession_item.cpp:594"]
    f13_4 --> f13_5["SetAVPlaybackState<br/>services/session/server/avsession_item.cpp:835"]
    f13_5 --> f13_6["ReadMetaDataAVQueueImg<br/>services/session/server/avsession_item.cpp:2748"]
    f13_6 --> f13_7["ReadMetaDataImg<br/>services/session/server/avsession_item.cpp:2738"]
    f13_7 --> f13_8["CheckUseAVMetaData<br/>services/session/server/avsession_item.cpp:471"]
    f13_8 --> f13_9["GetPid<br/>services/session/server/avsession_item.cpp:3273"]
    f13_9 --> f13_10["ReadMediaAndAVQueueImg<br/>services/session/server/avsession_item.cpp:571"]
    f13_10 --> f13_11["ReportMetadataChange<br/>services/session/server/avsession_item.cpp:3689"]
    f13_11 --> f13_12["UpdateMetaData<br/>services/session/server/avsession_item.cpp:531"]
    f13_12 --> f13_13["省略18步<br/>...:NNN"]
```

### CastAudioFromRemote (flow 5)
```mermaid
flowchart LR
    f5_1["CastAudioFromRemote<br/>services/session/server/avsession_item.cpp:3474"] --> f5_2["Activate<br/>services/session/server/avsession_item.cpp:1402"]
    f5_2 --> f5_3["AddSupportCommand<br/>services/session/server/avsession_item.cpp:1464"]
    f5_3 --> f5_4["GetOutputDevice<br/>services/session/server/avsession_item.cpp:3443"]
    f5_4 --> f5_5["SetOutputDevice<br/>services/session/server/avsession_item.cpp:3411"]
    f5_5 --> f5_6["GetBundleName<br/>services/session/server/avsession_item.cpp:3294"]
    f5_6 --> f5_7["GetSessionId<br/>services/session/server/avsession_item.cpp:143"]
    f5_7 --> f5_8["GetSessionType<br/>services/session/server/avsession_item.cpp:148"]
    f5_8 --> f5_9["AddSessionCommandToCast<br/>services/session/server/avsession_item.cpp:1850"]
    f5_9 --> f5_10["ProcessFrontSession<br/>services/session/server/avsession_item.cpp:334"]
    f5_10 --> f5_11["ReportCommandChange<br/>services/session/server/avsession_item.cpp:3710"]
    f5_11 --> f5_12["GetDescriptor<br/>services/session/server/avsession_item.cpp:2695"]
    f5_12 --> f5_13["HandleOutputDeviceChange<br/>services/session/server/avsession_item.cpp:3402"]
    f5_13 --> f5_14["HandleCastValidCommandChange<br/>services/session/server/avsession_item.cpp:1960"]
    f5_14 --> f5_15["省略8步<br/>...:NNN"]
```

### CastAudioForAll (flow 3)
```mermaid
flowchart LR
    f3_1["CastAudioForAll<br/>services/session/server/avsession_service.cpp:4027"] --> f3_2["CastAudio<br/>services/session/server/avsession_service.cpp:3885"]
    f3_2 --> f3_3["IsLocalDevice<br/>services/session/server/avsession_service.cpp:3728"]
    f3_3 --> f3_4["CastAudioProcess<br/>services/session/server/avsession_service.cpp:3901"]
    f3_4 --> f3_5["SetBasicInfo<br/>services/session/server/avsession_service.cpp:3788"]
    f3_5 --> f3_6["GetLocalNetworkId<br/>services/session/server/avsession_service.cpp:3741"]
    f3_6 --> f3_7["CancelCastAudioInner<br/>services/session/server/avsession_service.cpp:3978"]
    f3_7 --> f3_8["CastAudioInner<br/>services/session/server/avsession_service.cpp:3927"]
    f3_8 --> f3_9["GetDeviceInfo<br/>services/session/server/avsession_service.cpp:3840"]
    f3_9 --> f3_10["SetDeviceInfo<br/>services/session/server/avsession_service.cpp:3802"]
    f3_10 --> f3_11["省略88步<br/>...:NNN"]
```

### GetAVCastControllerInner (flow 4)
```mermaid
flowchart LR
    f4_1["GetAVCastControllerInner<br/>services/session/server/avsession_item.cpp:1312"] --> f4_2["GetDescriptor<br/>services/session/server/avsession_item.cpp:2695"]
    f4_2 --> f4_3["GetSessionId<br/>services/session/server/avsession_item.cpp:143"]
    f4_3 --> f4_4["GetSpid<br/>services/session/server/avsession_item.cpp:2543"]
    f4_4 --> f4_5["InitAVCastControllerProxy<br/>services/session/server/avsession_item.cpp:1248"]
    f4_5 --> f4_6["InitializeCastCommands<br/>services/session/server/avsession_item.cpp:1812"]
    f4_6 --> f4_7["ReportAVCastControllerInfo<br/>services/session/server/avsession_item.cpp:1262"]
    f4_7 --> f4_8["ReportOnPlayerError<br/>services/session/server/avsession_item.cpp:1271"]
    f4_8 --> f4_9["SearchSpidInCapability<br/>services/session/server/avsession_item.cpp:2549"]
    f4_9 --> f4_10["SetCastControllerCallbackForCastCap<br/>services/session/server/avsession_item.cpp:1354"]
    f4_10 --> f4_11["SetSpid<br/>services/session/server/avsession_item.cpp:2528"]
    f4_11 --> f4_12["dealValidCallback<br/>services/session/server/avsession_item.cpp:1282"]
    f4_12 --> f4_13["AddSessionCommandToCast<br/>services/session/server/avsession_item.cpp:1850"]
    f4_13 --> f4_14["省略13步<br/>...:NNN"]
```

### RegisterListenerStreamToCast (flow 27)
```mermaid
flowchart LR
    f27_1["RegisterListenerStreamToCast<br/>services/session/server/avsession_item.cpp:1772"] --> f27_2["DoContinuousTaskRegister<br/>services/session/server/avsession_item.cpp:3573"]
    f27_2 --> f27_3["GetSessionId<br/>services/session/server/avsession_item.cpp:143"]
    f27_3 --> f27_4["InitAVCastControllerProxy<br/>services/session/server/avsession_item.cpp:1248"]
    f27_4 --> f27_5["SetCastHandle<br/>services/session/server/avsession_item.cpp:2379"]
    f27_5 --> f27_6["StartCast<br/>services/session/server/avsession_item.cpp:1995"]
    f27_6 --> f27_7["UpdateCastDeviceMap<br/>services/session/server/avsession_item.cpp:3519"]
    f27_7 --> f27_8["GetPid<br/>services/session/server/avsession_item.cpp:3273"]
    f27_8 --> f27_9["GetUid<br/>services/session/server/avsession_item.cpp:3278"]
    f27_9 --> f27_10["IsCasting<br/>services/session/server/avsession_item.cpp:3631"]
    f27_10 --> f27_11["CastAddToCollaboration<br/>services/session/server/avsession_item.cpp:1987"]
    f27_11 --> f27_12["StopCast<br/>services/session/server/avsession_item.cpp:2332"]
    f27_12 --> f27_13["SubStartCast<br/>services/session/server/avsession_item.cpp:2050"]
    f27_13 --> f27_14["省略8步<br/>...:NNN"]
```

## 逐步错误上报

### CastAudioForAll → CastAudioInner (flow 3)
- **步骤**：`CastAudioInner (services/session/server/avsession_service.cpp:3927)`
- **上报**：`SESSION_CAST`（BEHAVIOR/MINOR）
- **错误条件**：CastAudioToRemote 成功后写投屏行为埋点（成功路径埋点，非错误；若 ProcessCastAudioCommand/GetAllCapability/CastAudioToRemote 任一 CHECK_AND_RETURN_RET_LOG 失败则提前返回不达此埋点，:3951/:3954/:3956）
- **file:line**：`services/session/server/avsession_service.cpp:3957`

### StartCast（投屏发起，与 CastAudioForAll 同域）
- **步骤**：`StartCast (services/session/server/avsession_service_ext.cpp:~580)`
- **上报**：`SESSION_CAST`（BEHAVIOR/MINOR）
- **错误条件**：投屏建立成功后写埋点；若 ReportStartCastEnd 失败（:597 CHECK_AND_RETURN_RET_LOG）提前返回不写
- **file:line**：`services/session/server/avsession_service_ext.cpp:602`

### CastSession 创建回调
- **步骤**：`NotifyCastSession… (services/session/server/avsession_service_ext.cpp:~390)`
- **上报**：`SESSION_CAST`（BEHAVIOR/MINOR）
- **错误条件**：远端 cast 会话创建回调路径埋点
- **file:line**：`services/session/server/avsession_service_ext.cpp:402`

### CastAudioToRemote → 远端 SetAVMetaData 投递
- **步骤**：`RemoteSessionSourceImpl::SetAVMetaData (services/session/server/remote/remote_session_source_impl.cpp:~140)`
- **上报**：`REMOTE_CONTROL_FAILED`（FAULT/MINOR）
- **错误条件**：`syncer->PutAVMetaData()` 返回非 AVSESSION_SUCCESS（远端投递超时/IPC 失败）
- **file:line**：`services/session/server/remote/remote_session_source_impl.cpp:152`

### CastAudioToRemote → 远端 SetAVPlaybackState 投递
- **步骤**：`RemoteSessionSourceImpl::SetAVPlaybackState (services/session/server/remote/remote_session_source_impl.cpp:166)`
- **上报**：`REMOTE_CONTROL_FAILED`（FAULT/MINOR）
- **错误条件**：`syncer->PutAVPlaybackState()` 返回非成功（超时）
- **file:line**：`services/session/server/remote/remote_session_source_impl.cpp:179`

### CastAudioToRemote → 远端 SetAVQueueTitle 投递
- **步骤**：`RemoteSessionSourceImpl::SetAVQueueTitle (services/session/server/remote/remote_session_source_impl.cpp:~244)`
- **上报**：`REMOTE_CONTROL_FAILED`（FAULT/MINOR）
- **错误条件**：`syncer->PutAVQueueTitle()` 返回非成功（超时）
- **file:line**：`services/session/server/remote/remote_session_source_impl.cpp:252`

### CastAudioToRemote → 远端断连通知
- **步骤**：`RemoteSessionSourceImpl::RegisterDisconnectNotifier (services/session/server/remote/remote_session_source_impl.cpp:59)`
- **上报**：`REMOTE_CONTROL_FAILED`（FAULT/MINOR）
- **错误条件**：远端设备断开（`ERROR_TYPE=REMOTE_DISCONNECTED`）
- **file:line**：`services/session/server/remote/remote_session_source_impl.cpp:64`

### CastAudioFromRemote → sink 端断连通知
- **步骤**：`RemoteSessionSinkImpl::RegisterDisconnectNotifier (services/session/server/remote/remote_session_sink_impl.cpp:57)`
- **上报**：`REMOTE_CONTROL_FAILED`（FAULT/MINOR）
- **错误条件**：sink 侧远端设备断开（`ERROR_TYPE=REMOTE_DISCONNECTED`）
- **file:line**：`services/session/server/remote/remote_session_sink_impl.cpp:60`

### CastAudioFromRemote → sink 端 SetControlCommand 投递
- **步骤**：`RemoteSessionSinkImpl::SetControlCommand (services/session/server/remote/remote_session_sink_impl.cpp:149)`
- **上报**：`REMOTE_CONTROL_FAILED`（FAULT/MINOR）
- **错误条件**：`syncer->PutControlCommand()` 返回非成功（超时）
- **file:line**：`services/session/server/remote/remote_session_sink_impl.cpp:154`

### HwCastStreamPlayer 控制命令投递
- **步骤**：`HwCastStreamPlayer::SendControlCommand (services/session/server/hw_cast_stream_player.cpp:75)`
- **上报**：`REMOTE_CONTROL_FAILED`（FAULT/MINOR）
- **错误条件**：`streamPlayer_` 为空（`ERROR_TYPE=INNER_ERROR`，远端连接不存在）
- **file:line**：`services/session/server/hw_cast_stream_player.cpp:82`

### HwCastStreamPlayer 非法命令
- **步骤**：`HwCastStreamPlayer::SendControlCommand (services/session/server/hw_cast_stream_player.cpp:167)`
- **上报**：`REMOTE_CONTROL_FAILED`（FAULT/MINOR）
- **错误条件**：switch default 分支命中（`ERROR_TYPE=INNER_ERROR`，invalid command）
- **file:line**：`services/session/server/hw_cast_stream_player.cpp:169`

### 投屏控制时延埋点（断连时上报）
- **步骤**：`AVSessionSysEvent::ReportSessionCastControl (utils/src/avsession_sysevent.cpp:388)`
- **上报**：`SESSION_CAST_CONTROL`（BEHAVIOR/CRITICAL）
- **错误条件**：投屏控制信息表中存在该 sessionId 且触发上报（CONTROL_TYPE/各时延字段），断连时落盘
- **file:line**：`utils/src/avsession_sysevent.cpp:398`

### GetAVCastControllerInner → 行为埋点
- **步骤**：`ReportAVCastControllerInfo (services/session/server/avsession_item.cpp:1262)`
- **上报**：`SESSION_API_BEHAVIOR`（BEHAVIOR/CRITICAL，半错误带 ERROR_CODE/ERROR_MSG）
- **错误条件**：投屏控制器信息上报行为埋点
- **file:line**：`services/session/server/avsession_item.cpp:1264`

### GetAVCastControllerInner → 播放器错误上报
- **步骤**：`ReportOnPlayerError (services/session/server/avsession_item.cpp:1271)`
- **上报**：`SESSION_API_BEHAVIOR`（BEHAVIOR/CRITICAL）
- **错误条件**：远端播放器错误回调
- **file:line**：`services/session/server/avsession_item.cpp:1273`

## 错误目录

<!-- ERR: SESSION_CAST | BEHAVIOR | MINOR | CastAudioForAll | services/session/server/avsession_service.cpp:3957 | CastAudioToRemote 成功后投屏行为埋点 -->
<!-- ERR: SESSION_CAST | BEHAVIOR | MINOR | CastAudioForAll | services/session/server/avsession_service_ext.cpp:602 | StartCast 建立成功后投屏行为埋点 -->
<!-- ERR: SESSION_CAST | BEHAVIOR | MINOR | CastAudioFromRemote | services/session/server/avsession_service_ext.cpp:402 | 远端 cast 会话创建回调埋点 -->
<!-- ERR: REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:64 | 远端设备断开 REMOTE_DISCONNECTED -->
<!-- ERR: REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:152 | PutAVMetaData 返回非成功 TIME_OUT -->
<!-- ERR: REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:179 | PutAVPlaybackState 返回非成功 TIME_OUT -->
<!-- ERR: REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:204 | PutExtras 返回非成功 TIME_OUT -->
<!-- ERR: REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:228 | PutAVQueueImage 返回非成功 TIME_OUT -->
<!-- ERR: REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:252 | PutAVQueueTitle 返回非成功 TIME_OUT -->
<!-- ERR: REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:276 | PutCommonCommand 返回非成功 TIME_OUT -->
<!-- ERR: REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioFromRemote | services/session/server/remote/remote_session_sink_impl.cpp:60 | sink 侧远端断开 REMOTE_DISCONNECTED -->
<!-- ERR: REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioFromRemote | services/session/server/remote/remote_session_sink_impl.cpp:154 | PutControlCommand 返回非成功 TIME_OUT -->
<!-- ERR: REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioFromRemote | services/session/server/remote/remote_session_sink_impl.cpp:172 | PutCommonCommand 返回非成功 TIME_OUT -->
<!-- ERR: REMOTE_CONTROL_FAILED | FAULT | MINOR | GetAVCastControllerInner | services/session/server/hw_cast_stream_player.cpp:82 | streamPlayer_ 为空 INNER_ERROR -->
<!-- ERR: REMOTE_CONTROL_FAILED | FAULT | MINOR | GetAVCastControllerInner | services/session/server/hw_cast_stream_player.cpp:169 | 非法控制命令 INNER_ERROR -->
<!-- ERR: SESSION_CAST_CONTROL | BEHAVIOR | CRITICAL | RegisterListenerStreamToCast | utils/src/avsession_sysevent.cpp:398 | 投屏控制时延埋点 断连时上报 -->
<!-- ERR: SESSION_API_BEHAVIOR | BEHAVIOR | CRITICAL | GetAVCastControllerInner | services/session/server/avsession_item.cpp:1264 | 投屏控制器信息上报 -->
<!-- ERR: SESSION_API_BEHAVIOR | BEHAVIOR | CRITICAL | GetAVCastControllerInner | services/session/server/avsession_item.cpp:1273 | 远端播放器错误回调 -->

| 事件名 | 类型 | 级别 | 触发流 | 上报 file:line | 错误条件 |
|---|---|---|---|---|---|
| SESSION_CAST | BEHAVIOR | MINOR | CastAudioForAll | services/session/server/avsession_service.cpp:3957 | CastAudioToRemote 成功后投屏行为埋点 |
| SESSION_CAST | BEHAVIOR | MINOR | CastAudioForAll | services/session/server/avsession_service_ext.cpp:602 | StartCast 建立成功后投屏行为埋点 |
| SESSION_CAST | BEHAVIOR | MINOR | CastAudioFromRemote | services/session/server/avsession_service_ext.cpp:402 | 远端 cast 会话创建回调埋点 |
| REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:64 | 远端设备断开 REMOTE_DISCONNECTED |
| REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:152 | PutAVMetaData 返回非成功 TIME_OUT |
| REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:179 | PutAVPlaybackState 返回非成功 TIME_OUT |
| REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:204 | PutExtras 返回非成功 TIME_OUT |
| REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:228 | PutAVQueueImage 返回非成功 TIME_OUT |
| REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:252 | PutAVQueueTitle 返回非成功 TIME_OUT |
| REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioToRemote | services/session/server/remote/remote_session_source_impl.cpp:276 | PutCommonCommand 返回非成功 TIME_OUT |
| REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioFromRemote | services/session/server/remote/remote_session_sink_impl.cpp:60 | sink 侧远端断开 REMOTE_DISCONNECTED |
| REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioFromRemote | services/session/server/remote/remote_session_sink_impl.cpp:154 | PutControlCommand 返回非成功 TIME_OUT |
| REMOTE_CONTROL_FAILED | FAULT | MINOR | CastAudioFromRemote | services/session/server/remote/remote_session_sink_impl.cpp:172 | PutCommonCommand 返回非成功 TIME_OUT |
| REMOTE_CONTROL_FAILED | FAULT | MINOR | GetAVCastControllerInner | services/session/server/hw_cast_stream_player.cpp:82 | streamPlayer_ 为空 INNER_ERROR |
| REMOTE_CONTROL_FAILED | FAULT | MINOR | GetAVCastControllerInner | services/session/server/hw_cast_stream_player.cpp:169 | 非法控制命令 INNER_ERROR |
| SESSION_CAST_CONTROL | BEHAVIOR | CRITICAL | RegisterListenerStreamToCast | utils/src/avsession_sysevent.cpp:398 | 投屏控制时延埋点 断连时上报 |
| SESSION_API_BEHAVIOR | BEHAVIOR | CRITICAL | GetAVCastControllerInner | services/session/server/avsession_item.cpp:1264 | 投屏控制器信息上报 |
| SESSION_API_BEHAVIOR | BEHAVIOR | CRITICAL | GetAVCastControllerInner | services/session/server/avsession_item.cpp:1273 | 远端播放器错误回调 |
