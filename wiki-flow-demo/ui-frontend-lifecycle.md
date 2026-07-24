---
title: 前端 UI 生命周期
business_domain: UIFrontend
lifecycle: AVCastPicker 前端 UI 构建器生命周期:扫描状态变更/系统标题/大字体标题/房间名与音量构建
flows: [35:homeMusicScanStatusChange, 36:HomeMusicSystemTitleBuilder, 37:BigFontHomeMusicSystemTitleBuilder, 38:RoomNameAndVolumeBuilder]
entry_points: [homeMusicScanStatusChange, HomeMusicSystemTitleBuilder, BigFontHomeMusicSystemTitleBuilder, RoomNameAndVolumeBuilder]
hisysevent_events: []
crg_commit: a4ec47de96f7
last_updated: 2026-07-24
source_repo: multimedia_av_session
---

# 前端 UI 生命周期

## 概述
本域为 `avpicker/avpicker.js` 中 AVCastPicker 前端 UI 构建逻辑：`homeMusicScanStatusChange` 响应扫描状态变更并维护房间选中态；`HomeMusicSystemTitleBuilder`/`BigFontHomeMusicSystemTitleBuilder` 构建系统音乐标题（全选事件/空房间服务/全选状态）；`RoomNameAndVolumeBuilder` 构建房间名与音量滑块。典型报错方向：前端 JS 逻辑为本地状态计算，**无 HiSysEvent/hilog 上报**——错误以 JS 运行时异常或上游 napi 接口返回值（如 `napi_invalid_arg`）的形式体现，由调用方处理。本域无 FAULT/SECURITY 级 HiSysEvent 上报。

## 调用序列

### homeMusicScanStatusChange (flow 35)
```mermaid
flowchart LR
    A["homeMusicScanStatusChange<br/>avpicker/avpicker.js:944"] --> B["clearTimer<br/>avpicker/avpicker.js:1005"]
    A --> C["scanDelayChange<br/>avpicker/avpicker.js:964"]
    A --> D["setAllRoomSelectStatusPending<br/>avpicker/avpicker.js:1018"]
    A --> E["roomSelectStatusPendingInit<br/>avpicker/avpicker.js:1011"]
    A --> F["checkRoomIsSelect<br/>avpicker/avpicker.js:986"]
```

### HomeMusicSystemTitleBuilder (flow 36)
```mermaid
flowchart LR
    A["HomeMusicSystemTitleBuilder<br/>avpicker/avpicker.js:1617"] --> B["allSelectOnClickEven<br/>avpicker/avpicker.js:1096"]
    A --> C["createNullRoomService<br/>avpicker/avpicker.js:867"]
    A --> D["getCurrIsAllSelectStatus<br/>avpicker/avpicker.js:993"]
    A --> E["roomSelectStatusPendingInit<br/>avpicker/avpicker.js:1011"]
    A --> F["setAllRoomSelectStatusPending<br/>avpicker/avpicker.js:1018"]
    A --> G["checkRoomIsSelect<br/>avpicker/avpicker.js:986"]
```

### BigFontHomeMusicSystemTitleBuilder (flow 37)
```mermaid
flowchart LR
    A["BigFontHomeMusicSystemTitleBuilder<br/>avpicker/avpicker.js:1651"] --> B["allSelectOnClickEven<br/>avpicker/avpicker.js:1096"]
    A --> C["createNullRoomService<br/>avpicker/avpicker.js:867"]
    A --> D["getCurrIsAllSelectStatus<br/>avpicker/avpicker.js:993"]
    A --> E["roomSelectStatusPendingInit<br/>avpicker/avpicker.js:1011"]
    A --> F["setAllRoomSelectStatusPending<br/>avpicker/avpicker.js:1018"]
    A --> G["checkRoomIsSelect<br/>avpicker/avpicker.js:986"]
```

### RoomNameAndVolumeBuilder (flow 38)
```mermaid
flowchart LR
    A["RoomNameAndVolumeBuilder<br/>avpicker/avpicker.js:1786"] --> B["onSliderValueChange<br/>avpicker/avpicker.js:1041"]
    A --> C["findRoomMaxVolume<br/>avpicker/avpicker.js:976"]
    A --> D["roomMaxVolumeChange<br/>avpicker/avpicker.js:971"]
    A --> E["checkRoomIsSelect<br/>avpicker/avpicker.js:986"]
```

## 逐步错误上报
本域 4 条流均为 `avpicker/avpicker.js` 前端 JS 构建逻辑，全链路 **无 HiSysEvent / hilog 上报**（grep `HiSysEvent|HISYSEVENT|hilog` 在 `avpicker/avpicker.js` 无命中）。
- `homeMusicScanStatusChange`：清定时器/延迟扫描/置房间选中态，错误以未匹配的房间数据形式体现于 UI，无上报。
- `HomeMusicSystemTitleBuilder`/`BigFontHomeMusicSystemTitleBuilder`：全选点击/空房间服务/全选状态计算，无上报。
- `RoomNameAndVolumeBuilder`：滑块值变更/房间最大音量查找，无上报；若上游 `napi` 接口返回 `napi_invalid_arg`，由 `napi_utils.cpp`（见序列化域）侧返回，本域不产生日志。

## 错误目录

| 事件名 | 类型 | 级别 | 触发流 | 上报 file:line | 错误条件 |
|---|---|---|---|---|---|
| NONE | - | - | 前端 UI 生命周期 | - | 本域无 FAULT/SECURITY 级 HiSysEvent 上报(纯前端 JS 本地逻辑) |
<!-- ERR: NONE | - | - | 前端 UI 生命周期 | - | 本域无 FAULT/SECURITY 级 HiSysEvent 上报(纯前端 JS 本地逻辑) -->

## 下钻锚点
- 扫描状态变更：`avpicker/avpicker.js:944`（homeMusicScanStatusChange）
- 系统标题构建：`avpicker/avpicker.js:1617`（HomeMusicSystemTitleBuilder）/ `:1651`（BigFontHomeMusicSystemTitleBuilder）
- 房间名与音量：`avpicker/avpicker.js:1786`（RoomNameAndVolumeBuilder）
- 公共选中态：`avpicker/avpicker.js:986`（checkRoomIsSelect）/ `:1018`（setAllRoomSelectStatusPending）
