# BÁO CÁO PHÂN CHIA CÔNG VIỆC
# DỰ ÁN SMART KITCHEN IOT

---

**Ngày lập:** 09/01/2026  
**Số thành viên:** 3 người  
**Phương pháp chia:** Theo Module (Feature-based)

---

## 1. TỔNG QUAN PHÂN CHIA

| Thành viên | Module phụ trách | IoT | Backend | Frontend |
|------------|------------------|-----|---------|----------|
| **Người 1** | 🔥 BẾP (Stove) | ✅ | ✅ | ✅ |
| **Người 2** | ❄️ TỦ LẠNH (Fridge) | ✅ | ✅ | ✅ |
| **Người 3** | 🚨 CẢM BIẾN + AUTH | ✅ | ✅ | ✅ |

---

## 2. CHI TIẾT NGƯỜI 1: MODULE BẾP (STOVE)

### 2.1. Files đảm nhiệm

| Layer | File | Mô tả |
|-------|------|-------|
| IoT | `front-end/stove.js` | Simulator bếp từ |
| Backend | `server.js` (phần stove) | API command, lưu history |
| Backend | `models/TemperatureHistory.js` | Schema lịch sử nhiệt độ |
| Frontend | `components/DeviceCard.js` | UI điều khiển bếp |
| Frontend | `components/TemperatureChart.js` | Biểu đồ nhiệt độ |
| Frontend | `src/socket.js` | Socket.IO client |

### 2.2. Nhiệm vụ IoT

- Viết `stove.js` - mô phỏng bếp từ
- Kết nối MQTT broker
- Subscribe topic: `home/kitchen/stove{N}/command`
- Publish topic: `home/kitchen/stove{N}/status`
- Logic vật lý: 9 level nhiệt độ (30°C → 300°C)
- Xử lý lệnh: POWER ON/OFF, SET_LEVEL

### 2.3. Nhiệm vụ Backend

- API `POST /api/device/command` (xử lý lệnh bếp)
- Nhận MQTT status từ bếp → emit Socket.IO
- Lưu lịch sử nhiệt độ bếp vào MongoDB
- API `GET /api/devices/:id/temperature-history`

### 2.4. Nhiệm vụ Frontend

- `DeviceCard.js` - Card điều khiển bếp
- Nút BẬT/TẮT, slider level 1-9
- Hiển thị nhiệt độ realtime
- `TemperatureChart.js` - Biểu đồ nhiệt độ (Chart.js)

### 2.5. MQTT Data Format

```json
// Bếp gửi lên (status)
{
  "power": "ON",
  "temperature": 150.5,
  "target_temp": 180.0,
  "level": 5
}

// Server gửi xuống (command)
{ "cmd": "POWER", "val": "ON" }
{ "cmd": "SET_LEVEL", "val": 5 }
```

---

## 3. CHI TIẾT NGƯỜI 2: MODULE TỦ LẠNH (FRIDGE)

### 3.1. Files đảm nhiệm

| Layer | File | Mô tả |
|-------|------|-------|
| IoT | `front-end/fridge.js` | Simulator tủ lạnh |
| Backend | `server.js` (phần fridge) | API CRUD, logic auto-close |
| Backend | `models/Device.js` | Schema Device |
| Frontend | `components/FridgeCard.js` | UI điều khiển tủ lạnh |
| Frontend | `components/DeviceManager.js` | Modal quản lý device |
| Frontend | `src/api.js` | REST API client |

### 3.2. Nhiệm vụ IoT

- Viết `fridge.js` - mô phỏng tủ lạnh
- Kết nối MQTT broker
- Subscribe: `home/kitchen/fridge{N}/command`
- Publish: `home/kitchen/fridge{N}/status`
- Logic vật lý:
  - Mở cửa → nhiệt độ tăng dần (về 30°C)
  - Đóng cửa → nhiệt độ giảm về target
- Xử lý lệnh: SET_DOOR, SET_TEMP

### 3.3. Nhiệm vụ Backend

- API CRUD `/api/devices` (GET, POST, PUT, DELETE)
- Logic AUTO-CLOSE:
  - Nếu temp > 15°C + cửa mở > 15 phút → tự đóng
- Emit `safety_alert` qua Socket.IO
- Lưu lịch sử nhiệt độ tủ lạnh

### 3.4. Nhiệm vụ Frontend

- `FridgeCard.js` - Card điều khiển tủ lạnh
- Nút MỞ/ĐÓNG CỬA, slider nhiệt độ 0-10°C
- `DeviceManager.js` - Modal quản lý thiết bị
- Form thêm/sửa/xóa device

### 3.5. MQTT Data Format

```json
// Tủ lạnh gửi lên (status)
{
  "current_temp": 5.0,
  "target_temp": 4.0,
  "door": "CLOSED"
}

// Server gửi xuống (command)
{ "cmd": "SET_DOOR", "val": "OPEN" }
{ "cmd": "SET_TEMP", "val": 4 }
```

---

## 4. CHI TIẾT NGƯỜI 3: MODULE CẢM BIẾN + AUTH

### 4.1. Files đảm nhiệm

| Layer | File | Mô tả |
|-------|------|-------|
| IoT | `embed/68.ino` | ESP32 firmware (FreeRTOS) |
| IoT | `scripts/manage-simulators.js` | Quản lý PM2 |
| Backend | `server.js` (phần auth + safety) | Login, Auto-off gas |
| Backend | `models/User.js` | Schema User + bcrypt |
| Frontend | `components/Login.js` | Form đăng nhập |
| Frontend | `components/SensorCard.js` | UI cảm biến |
| Config | `ecosystem.config.js` | PM2 config |

### 4.2. Nhiệm vụ IoT

- Viết `68.ino` - Firmware ESP32 với FreeRTOS
- 3 Tasks song song:
  - **TaskSensor:** Đọc MQ-2 + Flame mỗi 100ms, bật còi/đèn
  - **TaskMQTT:** Gửi data mỗi 2 giây
  - **TaskTelegram:** Gửi cảnh báo khi nguy hiểm
- `manage-simulators.js` - Auto start/stop PM2 processes

### 4.3. Nhiệm vụ Backend

- API `POST /api/register` - Đăng ký user
- API `POST /api/login` - Đăng nhập, trả JWT
- Middleware `authMiddleware` - Verify token
- Logic AUTO-OFF GAS:
  - Nhận data `gas="DETECTED"` từ sensor
  - Tìm tất cả bếp của user đó
  - Gửi lệnh POWER OFF đến từng bếp
- Emit `safety_alert` qua Socket.IO

### 4.4. Nhiệm vụ Frontend

- `Login.js` - Form đăng nhập/đăng ký
- Toggle giữa Login và Register mode
- `SensorCard.js` - Hiển thị trạng thái Gas/Fire
- Đổi màu đỏ khi DETECTED
- Xử lý hiển thị safety_alert popup

### 4.5. MQTT Data Format

```json
// ESP32 gửi lên (status)
{
  "gas": "DETECTED",
  "fire": "SAFE"
}
```

---

## 5. FILES CHUNG VÀ PHÂN CÔNG

| File | Người chính | Ghi chú |
|------|-------------|---------|
| `server.js` | Chia theo section | Merge code cuối |
| `main.js` | Người 3 | Entry point |
| `api.js` | Người 2 | REST client |
| `socket.js` | Người 1 | Socket.IO client |
| `Dashboard.js` | Cả 3 | Integrate components |
| `index.html` | Người 2 | HTML structure |
| `styles.css` | Cả 3 | Mỗi người thêm styles |

---

## 6. PHÂN CHIA SERVER.JS

### Người 1 phụ trách:
- API `/api/device/command`
- API `/api/temperature-history`
- Lưu temperature history vào DB
- MQTT connection + emit socket

### Người 2 phụ trách:
- API CRUD `/api/devices`
- Logic AUTO-CLOSE fridge
- Device cache

### Người 3 phụ trách:
- Import, config, khởi tạo
- `authMiddleware`
- API `/api/register`, `/api/login`
- Logic AUTO-OFF khi gas DETECTED

---

## 7. SƠ ĐỒ TÍCH HỢP

```
┌─────────────────────────────────────────────────────────┐
│                   MQTT BROKER                           │
└─────────────────────────────────────────────────────────┘
       ▲              ▲              ▲
       │              │              │
  ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
  │ ESP32   │   │ Stove   │   │ Fridge  │
  │ Sensor  │   │ Sim     │   │ Sim     │
  │(Người 3)│   │(Người 1)│   │(Người 2)│
  └─────────┘   └─────────┘   └─────────┘
       │              │              │
       └──────────────┼──────────────┘
                      ▼
         ┌────────────────────────┐
         │      SERVER.JS         │
         │  ┌──────┬──────┬─────┐ │
         │  │Auth  │Stove │Fridge│ │
         │  │(P.3) │(P.1) │(P.2) │ │
         │  └──────┴──────┴─────┘ │
         └────────────┬───────────┘
                      │ Socket.IO
                      ▼
         ┌────────────────────────┐
         │      DASHBOARD         │
         │  ┌──────┬──────┬─────┐ │
         │  │Sensor│Device│Fridge│ │
         │  │Card  │Card  │Card  │ │
         │  │(P.3) │(P.1) │(P.2) │ │
         │  └──────┴──────┴─────┘ │
         └────────────────────────┘
```

---

## 8. SO SÁNH WORKLOAD

| Tiêu chí | Người 1 | Người 2 | Người 3 |
|----------|---------|---------|---------|
| IoT files | 1 | 1 | 2 |
| Backend logic | Temp history | Auto-close + CRUD | Auth + Auto-off |
| Frontend components | 2 | 2 | 2 |
| Phần cứng | ❌ | ❌ | ✅ ESP32 |
| Độ phức tạp | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 9. CHECKLIST CÔNG VIỆC

### Người 1 - Module Bếp
- [ ] `stove.js` - Simulator hoàn chỉnh
- [ ] MQTT pub/sub cho stove
- [ ] API `/api/device/command`
- [ ] API `/api/temperature-history`
- [ ] Lưu history vào DB
- [ ] `DeviceCard.js` - UI bếp
- [ ] `TemperatureChart.js` - Biểu đồ
- [ ] `socket.js` - Socket.IO client

### Người 2 - Module Tủ lạnh
- [ ] `fridge.js` - Simulator hoàn chỉnh
- [ ] MQTT pub/sub cho fridge
- [ ] API CRUD `/api/devices`
- [ ] Logic auto-close fridge
- [ ] `Device.js` - Schema
- [ ] `FridgeCard.js` - UI tủ lạnh
- [ ] `DeviceManager.js` - Modal
- [ ] `api.js` - REST client

### Người 3 - Module Sensor + Auth
- [ ] `68.ino` - ESP32 firmware
- [ ] FreeRTOS 3 tasks
- [ ] Telegram Bot cảnh báo
- [ ] API register/login
- [ ] JWT + authMiddleware
- [ ] Logic auto-off gas
- [ ] `User.js` - Schema
- [ ] `Login.js` - UI đăng nhập
- [ ] `SensorCard.js` - UI cảm biến
- [ ] `manage-simulators.js`

---

## 10. ĐỀ XUẤT TIMELINE (2 TUẦN)

| Tuần | Người 1 | Người 2 | Người 3 |
|------|---------|---------|---------|
| Tuần 1 | Stove simulator + DeviceCard | Fridge simulator + FridgeCard | ESP32 firmware + Login |
| Tuần 2 | API + Chart + Socket | API CRUD + DeviceManager | Auth + Safety logic |
| Cuối tuần 2 | **INTEGRATION & TESTING CHUNG** |

---

## 11. KẾT LUẬN

Cách phân chia này đảm bảo:

✅ **Cả 3 đều code IoT** (simulator hoặc ESP32)  
✅ **Cả 3 đều code Backend** (API + business logic)  
✅ **Cả 3 đều code Frontend** (UI components)  
✅ **Workload cân bằng** (~33% mỗi người)  
✅ **Học được full-stack IoT**  
✅ **Dễ tích hợp** (qua MQTT/API/Socket.IO)

---

*Báo cáo phân chia công việc - Smart Kitchen IoT Project*
