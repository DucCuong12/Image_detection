# BÁO CÁO PHÂN TÍCH HỆ THỐNG SMART KITCHEN IOT

## Thông tin chung
- **Tên dự án:** Smart Kitchen IoT
- **Ngày báo cáo:** 09/01/2026
- **Mô tả:** Hệ thống giám sát và điều khiển bếp thông minh với ESP32, MQTT, Node.js và Web Dashboard

---

# PHẦN 1: TỔNG QUAN KIẾN TRÚC HỆ THỐNG

## 1.1. Sơ đồ kiến trúc

```
┌─────────────────┐     MQTT      ┌─────────────────┐    Socket.IO    ┌─────────────────┐
│   ESP32 Node    │──────────────▶│   Node.js       │◀───────────────▶│   Web Dashboard │
│  (Gas/Flame)    │◀──────────────│   Backend       │                 │   (Browser)     │
└─────────────────┘               └────────┬────────┘                 └─────────────────┘
                                           │
┌─────────────────┐     MQTT               │ MongoDB
│   Simulators    │────────────────────────┤
│ (Stove/Fridge)  │◀───────────────────────┘
└─────────────────┘
```

## 1.2. Công nghệ sử dụng

| Tầng | Công nghệ | Mục đích |
|------|-----------|----------|
| **Embedded** | ESP32, FreeRTOS, C++ | Đọc cảm biến, gửi cảnh báo |
| **IoT Protocol** | MQTT (Mosquitto) | Giao tiếp giữa thiết bị và server |
| **Backend** | Node.js, Express, Socket.IO | Xử lý logic, API, realtime |
| **Frontend** | Vanilla JS, Chart.js | Giao diện người dùng |
| **Database** | MongoDB | Lưu trữ users, devices, history |

---

# PHẦN 2: MÔ TẢ CHI TIẾT TỪNG FILE

## 2.1. BACKEND (back-end/)

### 📄 server.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `back-end/server.js` |
| **Mục đích** | File chính của server - trung tâm xử lý toàn bộ hệ thống |
| **Chức năng chính** | - Khởi tạo Express server phục vụ API REST<br>- Kết nối MQTT broker để nhận/gửi message từ thiết bị<br>- Khởi tạo Socket.IO để gửi dữ liệu realtime xuống web<br>- Kết nối MongoDB để lưu trữ dữ liệu<br>- Xử lý logic an toàn (tự động tắt bếp khi phát hiện gas) |
| **API cung cấp** | POST /api/login, POST /api/register, GET/POST/PUT/DELETE /api/devices, POST /api/device/command |

### 📄 ecosystem.config.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `back-end/ecosystem.config.js` |
| **Mục đích** | Cấu hình PM2 để chạy server production |
| **Chức năng chính** | - Giới hạn memory 1GB, tự động restart khi crash<br>- Cấu hình log files<br>- Auto-start khi server reboot |

### 📄 models/User.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `back-end/models/User.js` |
| **Mục đích** | Schema MongoDB cho User |
| **Chức năng chính** | - Định nghĩa cấu trúc: username, password, role<br>- Tự động hash password trước khi lưu (bcrypt)<br>- Method comparePassword() để verify đăng nhập |

### 📄 models/Device.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `back-end/models/Device.js` |
| **Mục đích** | Schema MongoDB cho Device (thiết bị) |
| **Chức năng chính** | - Lưu thông tin: name, type, mqtt_topic_root, user_id<br>- Liên kết device với user (mỗi user có devices riêng)<br>- Index unique cho mqtt_topic_root + user_id |

### 📄 models/TemperatureHistory.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `back-end/models/TemperatureHistory.js` |
| **Mục đích** | Schema MongoDB cho lịch sử nhiệt độ |
| **Chức năng chính** | - Lưu: device_id, temperature, timestamp<br>- TTL index: tự động xóa data cũ hơn 7 ngày |

### 📄 scripts/manage-simulators.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `back-end/scripts/manage-simulators.js` |
| **Mục đích** | Tự động quản lý các simulator qua PM2 |
| **Chức năng chính** | - Đọc danh sách devices từ DB<br>- Khởi động simulator mới khi thêm device<br>- Dừng simulator khi xóa device |

---

## 2.2. FRONTEND (front-end/)

### 📄 index.html
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `front-end/index.html` |
| **Mục đích** | Trang HTML chính của web dashboard |
| **Chức năng chính** | - Load thư viện: Socket.IO, Chart.js<br>- Chứa div#app để render React-like components<br>- Load main.js (ES Module) |

### 📄 stove.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `front-end/stove.js` |
| **Mục đích** | Simulator bếp từ - mô phỏng thiết bị bếp thật |
| **Chức năng chính** | - Kết nối MQTT broker<br>- Nhận lệnh từ server (POWER, SET_LEVEL)<br>- Mô phỏng vật lý: nhiệt độ tăng/giảm theo level<br>- Gửi trạng thái mỗi 1 giây qua MQTT |
| **MQTT Topics** | Subscribe: `{topic}/command`, Publish: `{topic}/status` |

### 📄 fridge.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `front-end/fridge.js` |
| **Mục đích** | Simulator tủ lạnh - mô phỏng thiết bị tủ lạnh thật |
| **Chức năng chính** | - Nhận lệnh: SET_DOOR, SET_TEMP<br>- Mô phỏng: mở cửa → nhiệt độ tăng, đóng cửa → nhiệt độ giảm<br>- Gửi trạng thái mỗi 2 giây |

### 📄 src/main.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `front-end/src/main.js` |
| **Mục đích** | Entry point của frontend app |
| **Chức năng chính** | - Kiểm tra token trong localStorage<br>- Routing: showLogin() hoặc showDashboard()<br>- Khởi tạo Socket.IO connection |

### 📄 src/api.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `front-end/src/api.js` |
| **Mục đích** | REST API client - gọi các API của backend |
| **Chức năng chính** | - login(), register(): Xác thực<br>- getDevices(), addDevice(), deleteDevice(): CRUD devices<br>- sendCommand(): Gửi lệnh điều khiển<br>- getTemperatureHistory(): Lấy lịch sử nhiệt độ |

### 📄 src/socket.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `front-end/src/socket.js` |
| **Mục đích** | Socket.IO client - nhận dữ liệu realtime |
| **Chức năng chính** | - Kết nối Socket.IO server<br>- Lắng nghe event 'device_update'<br>- Forward data đến callback để cập nhật UI |

### 📄 src/components/Login.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `front-end/src/components/Login.js` |
| **Mục đích** | Component form đăng nhập/đăng ký |
| **Chức năng chính** | - Render form với username/password<br>- Toggle giữa Login và Register mode<br>- Gọi callback onLogin/onRegister |

### 📄 src/components/Dashboard.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `front-end/src/components/Dashboard.js` |
| **Mục đích** | Component trang chính sau khi đăng nhập |
| **Chức năng chính** | - Fetch danh sách devices của user<br>- Render DeviceCard/FridgeCard/SensorCard tương ứng<br>- Đăng ký nhận Socket.IO updates<br>- Dispatch updates đến đúng card |

### 📄 src/components/DeviceCard.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `front-end/src/components/DeviceCard.js` |
| **Mục đích** | Component hiển thị và điều khiển BẾP |
| **Chức năng chính** | - Hiển thị: nhiệt độ, trạng thái power<br>- Nút BẬT/TẮT → gọi sendCommand()<br>- Slider chọn level 1-9<br>- Method updateState() để cập nhật từ socket |

### 📄 src/components/FridgeCard.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `front-end/src/components/FridgeCard.js` |
| **Mục đích** | Component hiển thị và điều khiển TỦ LẠNH |
| **Chức năng chính** | - Hiển thị: nhiệt độ khoang, trạng thái cửa<br>- Nút MỞ CỬA/ĐÓNG CỬA<br>- Slider đặt nhiệt độ target 0-10°C |

### 📄 src/components/SensorCard.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `front-end/src/components/SensorCard.js` |
| **Mục đích** | Component hiển thị dữ liệu CẢM BIẾN (từ ESP32) |
| **Chức năng chính** | - Hiển thị trạng thái Gas: SAFE/DETECTED<br>- Hiển thị trạng thái Fire: SAFE/DETECTED<br>- Đổi màu đỏ khi phát hiện nguy hiểm |

### 📄 src/components/DeviceManager.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `front-end/src/components/DeviceManager.js` |
| **Mục đích** | Modal quản lý thiết bị (thêm/sửa/xóa) |
| **Chức năng chính** | - Form thêm device mới<br>- Tự động generate MQTT topic<br>- Danh sách devices để sửa/xóa |

### 📄 src/components/TemperatureChart.js
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `front-end/src/components/TemperatureChart.js` |
| **Mục đích** | Biểu đồ nhiệt độ theo thời gian |
| **Chức năng chính** | - Fetch lịch sử nhiệt độ từ API<br>- Render Chart.js line chart<br>- Chọn khoảng thời gian: 8h/24h/3d/5d |

---

## 2.3. EMBEDDED (embed/)

### 📄 68.ino
| Thuộc tính | Mô tả |
|------------|-------|
| **Đường dẫn** | `embed/68.ino` |
| **Mục đích** | Firmware ESP32 - phần cứng cảm biến thật |
| **Chức năng chính** | - FreeRTOS với 3 tasks song song<br>- TaskSensor: Đọc cảm biến gas/lửa mỗi 100ms, bật còi/đèn<br>- TaskMQTT: Gửi data lên server mỗi 2 giây<br>- TaskTelegram: Gửi cảnh báo Telegram khi nguy hiểm |
| **Phần cứng** | MQ-2 (gas), Flame sensor, LED, Buzzer |

---

# PHẦN 3: USE CASE CHI TIẾT

## 3.1. USE CASE 1: ĐĂNG NHẬP VÀ XEM DASHBOARD

### Mô tả
User mở web browser, đăng nhập vào hệ thống và xem trạng thái các thiết bị.

### Luồng hoạt động

| Bước | Actor | Hành động | File xử lý | Kết quả |
|------|-------|-----------|------------|---------|
| 1 | User | Mở trình duyệt, truy cập http://server:3000 | `index.html` | Hiển thị trang web |
| 2 | System | Load main.js, kiểm tra token | `main.js` | Token không có → hiển thị Login |
| 3 | User | Nhập username/password, bấm "Vào Bếp" | `Login.js` | Gọi onLogin callback |
| 4 | System | Gửi POST /api/login | `api.js` | Gửi request đến server |
| 5 | Server | Verify credentials, tạo JWT | `server.js` | Trả về token |
| 6 | System | Lưu token vào localStorage | `main.js` | Chuyển sang Dashboard |
| 7 | System | Kết nối Socket.IO | `socket.js` | Sẵn sàng nhận realtime |
| 8 | System | Fetch GET /api/devices | `api.js` | Lấy danh sách devices |
| 9 | System | Render các DeviceCard | `Dashboard.js` | Hiển thị các thiết bị |
| 10 | System | Nhận device_update từ socket | `socket.js` | Cập nhật UI realtime |

### Sơ đồ sequence

```
User          Login.js       api.js        server.js      Dashboard.js    socket.js
 │               │              │              │               │              │
 │──nhập login──▶│              │              │               │              │
 │               │──onLogin()──▶│              │               │              │
 │               │              │──POST /api/login─▶           │              │
 │               │              │              │──verify──┐    │              │
 │               │              │              │◀─────────┘    │              │
 │               │              │◀───token─────│               │              │
 │               │◀─────────────│              │               │              │
 │               │              │              │               │              │
 │───────────────────────────showDashboard()──────────────────▶│              │
 │               │              │              │               │──connect()──▶│
 │               │              │──GET /api/devices───────────▶│              │
 │               │              │              │               │◀────────────│
 │               │              │              │               │──render()───│
 │◀──────────────────────────────hiển thị dashboard────────────│              │
```

---

## 3.2. USE CASE 2: TẠO DEVICE MỚI (THÊM BẾP)

### Mô tả
User đăng nhập và thêm một bếp từ mới vào hệ thống.

### Luồng hoạt động

| Bước | Actor | Hành động | File xử lý | Kết quả |
|------|-------|-----------|------------|---------|
| 1 | User | Bấm "Quản lý Thiết bị" | `Dashboard.js` | Mở modal |
| 2 | User | Chọn tab "Thêm Thiết bị" | `DeviceManager.js` | Hiển thị form |
| 3 | User | Nhập tên: "Bếp Nhà Bếp 2" | `DeviceManager.js` | Điền form |
| 4 | User | Chọn loại: "Bếp từ" | `DeviceManager.js` | Auto-generate topic |
| 5 | System | Tạo topic: "home/kitchen/stove2" | `DeviceManager.js` | Hiển thị trong input |
| 6 | User | Bấm "Thêm Thiết bị" | `DeviceManager.js` | Submit form |
| 7 | System | Gửi POST /api/devices | `api.js` | Request đến server |
| 8 | Server | Validate, lưu vào MongoDB | `server.js` + `Device.js` | Device được lưu |
| 9 | Server | Chạy manage-simulators.js | `manage-simulators.js` | Khởi động simulator |
| 10 | System | PM2 start stove.js với topic | `stove.js` | Simulator chạy |
| 11 | System | Refresh danh sách devices | `Dashboard.js` | Hiển thị bếp mới |

### Sơ đồ sequence

```
User      DeviceManager.js    api.js     server.js    Device.js   manage-simulators.js   stove.js
 │              │               │            │            │               │                 │
 │──điền form──▶│               │            │            │               │                 │
 │──submit─────▶│               │            │            │               │                 │
 │              │──addDevice()─▶│            │            │               │                 │
 │              │               │──POST /api/devices────▶│               │                 │
 │              │               │            │──new Device()────────────▶│               │
 │              │               │            │            │──save()──┐    │                 │
 │              │               │            │            │◀─────────┘    │                 │
 │              │               │            │──exec()───────────────────▶│                 │
 │              │               │            │               │──pm2.start()───────────────▶│
 │              │               │            │               │             │──connect MQTT─▶│
 │              │               │            │               │             │◀──subscribed──│
 │              │               │◀───device data─────────────│               │                 │
 │              │◀──────────────│            │            │               │                 │
 │◀─────────────│               │            │            │               │                 │
```

---

## 3.3. USE CASE 3: BẬT BẾP VÀ THEO DÕI NHIỆT ĐỘ

### Mô tả
User bật bếp từ, chỉnh level và theo dõi nhiệt độ tăng realtime.

### Luồng hoạt động

| Bước | Actor | Hành động | File xử lý | Kết quả |
|------|-------|-----------|------------|---------|
| 1 | User | Bấm nút [BẬT] trên DeviceCard | `DeviceCard.js` | Trigger click event |
| 2 | System | Gọi sendCommand(topic, 'POWER', 'ON') | `DeviceCard.js` | Chuẩn bị lệnh |
| 3 | System | POST /api/device/command | `api.js` | Gửi đến server |
| 4 | Server | mqttClient.publish(topic/command) | `server.js` | Gửi MQTT |
| 5 | Stove Simulator | Nhận lệnh, set state.power = "ON" | `stove.js` | Bếp bật |
| 6 | Stove Simulator | physicsLoop() tính nhiệt độ tăng | `stove.js` | temperature++ |
| 7 | Stove Simulator | Publish status lên MQTT | `stove.js` | Gửi trạng thái mới |
| 8 | Server | Nhận MQTT message | `server.js` | Parse data |
| 9 | Server | io.emit('device_update') | `server.js` | Gửi Socket.IO |
| 10 | System | socket.on('device_update') | `socket.js` | Nhận data |
| 11 | System | card.updateState(data) | `Dashboard.js` | Dispatch đến card |
| 12 | System | Cập nhật DOM: nhiệt độ, trạng thái | `DeviceCard.js` | UI hiển thị mới |

### Sơ đồ sequence

```
User    DeviceCard.js   api.js   server.js   MQTT Broker   stove.js   socket.js   Dashboard.js
 │           │            │          │            │            │           │            │
 │──[BẬT]───▶│            │          │            │            │           │            │
 │           │─sendCommand()────────▶│            │            │           │            │
 │           │            │──POST /api/device/command─────────▶│            │           │
 │           │            │          │──publish(topic/command)─▶│           │            │
 │           │            │          │            │──────────────▶│           │            │
 │           │            │          │            │     (nhận lệnh, bật bếp)  │            │
 │           │            │          │            │◀─publish(topic/status)───│           │            │
 │           │            │          │◀───────────│            │           │            │
 │           │            │          │──io.emit('device_update')──────────▶│            │
 │           │            │          │            │            │           │──onUpdate()─▶│
 │           │            │          │            │            │           │            │─card.updateState()
 │           │◀─────────────────────────────────────────────────────────────────────────│
 │◀──────────│            │          │            │            │           │            │
 │  (Thấy nhiệt độ tăng từ 30°C → 60°C → 90°C ...)            │           │            │
```

### Chi tiết tính toán nhiệt độ trong stove.js

```javascript
// Mỗi 1 giây, physicsLoop() được gọi
function physicsLoop() {
    if (state.power === "ON" && state.level > 0) {
        const maxTemp = 30 + (state.level * 30);  // Level 5 → max 180°C
        
        if (state.temperature < maxTemp) {
            const increment = 1.0 + (state.level * 0.5);  // Level cao → tăng nhanh hơn
            state.temperature += increment;
        }
    }
    
    // Gửi MQTT
    client.publish(`${DEVICE_TOPIC}/status`, JSON.stringify(state));
}
```

---

## 3.4. USE CASE 4: PHÁT HIỆN GAS VÀ TỰ ĐỘNG TẮT BẾP

### Mô tả
ESP32 phát hiện khí gas rò rỉ, server tự động tắt tất cả bếp của user đó và gửi cảnh báo.

### Luồng hoạt động

| Bước | Actor | Hành động | File xử lý | Kết quả |
|------|-------|-----------|------------|---------|
| 1 | ESP32 | MQ-2 sensor phát hiện gas | `68.ino` TaskSensor | g_isGas = true |
| 2 | ESP32 | Bật còi + đèn cảnh báo | `68.ino` TaskSensor | Cảnh báo tại chỗ |
| 3 | ESP32 | Publish {"gas":"DETECTED"} | `68.ino` TaskMQTT | Gửi MQTT |
| 4 | Server | Nhận MQTT message | `server.js` | Parse data |
| 5 | Server | Kiểm tra device.type === 'sensor_node' | `server.js` | Xác định là sensor |
| 6 | Server | Query tất cả stove_sim của user | `server.js` | Tìm bếp cần tắt |
| 7 | Server | Publish {cmd:'POWER', val:'OFF'} đến mỗi bếp | `server.js` | Gửi lệnh tắt |
| 8 | Stove Simulator | Nhận lệnh, tắt bếp | `stove.js` | state.power = "OFF" |
| 9 | Server | io.emit('safety_alert') | `server.js` | Gửi cảnh báo |
| 10 | Web Dashboard | Hiển thị popup cảnh báo | `Dashboard.js` | User thấy thông báo |
| 11 | ESP32 | Gửi tin nhắn Telegram | `68.ino` TaskTelegram | User nhận SMS |

### Sơ đồ sequence

```
MQ-2 Sensor   68.ino      MQTT Broker   server.js    Device DB    stove.js    Dashboard
     │           │             │            │            │            │            │
     │──LOW─────▶│             │            │            │            │            │
     │           │──bật còi/đèn│            │            │            │            │
     │           │──publish(sensor/status)─▶│            │            │            │
     │           │             │────────────▶│            │            │            │
     │           │             │            │──findOne(sensor_node)──▶│            │
     │           │             │            │◀───device data──────────│            │
     │           │             │            │──find(stove_sim, user_id)──────────▶│
     │           │             │            │◀───list of stoves───────│            │
     │           │             │            │──publish(stove1/command, OFF)──────▶│
     │           │             │            │──publish(stove2/command, OFF)──────▶│
     │           │             │            │            │            │◀───────────│
     │           │             │            │            │            │──power=OFF─│
     │           │             │            │──io.emit('safety_alert')────────────▶│
     │           │             │            │            │            │            │──alert()
     │           │──sendMessage(Telegram)──▶│            │            │            │
```

---

## 3.5. USE CASE 5: TỰ ĐỘNG ĐÓNG TỦ LẠNH KHI QUÁ NHIỆT

### Mô tả
Tủ lạnh mở cửa quá lâu (15 phút) khiến nhiệt độ > 15°C, server tự động đóng cửa.

### Luồng hoạt động

| Bước | Actor | Hành động | File xử lý | Kết quả |
|------|-------|-----------|------------|---------|
| 1 | User | Mở cửa tủ lạnh (quên đóng) | `FridgeCard.js` → `fridge.js` | door = "OPEN" |
| 2 | Fridge Sim | Nhiệt độ tăng dần (mở cửa) | `fridge.js` | current_temp tăng |
| 3 | Server | Nhận status, temp > 15°C & door = OPEN | `server.js` | Bắt đầu đếm |
| 4 | Server | Lưu highTempStartTime | `server.js` | Timer bắt đầu |
| 5 | ... | 15 phút trôi qua ... | | |
| 6 | Server | Kiểm tra elapsed >= 15 phút | `server.js` | Điều kiện thỏa |
| 7 | Server | Publish {cmd:'SET_DOOR', val:'CLOSED'} | `server.js` | Gửi lệnh |
| 8 | Fridge Sim | Nhận lệnh, đóng cửa | `fridge.js` | door = "CLOSED" |
| 9 | Server | io.emit('safety_alert') | `server.js` | Thông báo user |
| 10 | Dashboard | Hiển thị "Tủ lạnh đã tự động đóng" | `Dashboard.js` | User được thông báo |

---

# PHẦN 4: SƠ ĐỒ TỔNG HỢP LUỒNG DỮ LIỆU

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                           SMART KITCHEN IOT - DATA FLOW                              │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─────────────┐                                                    ┌─────────────┐ │
│  │   ESP32     │                                                    │   User      │ │
│  │ (Cảm biến)  │                                                    │  Browser    │ │
│  └──────┬──────┘                                                    └──────┬──────┘ │
│         │                                                                  │        │
│         │ MQTT                                                    HTTP/WS  │        │
│         │ publish                                                  REST    │        │
│         ▼                                                          API     ▼        │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐     ┌─────────┐ │
│  │    MQTT     │◀────────▶│   SERVER    │◀────────▶│   MongoDB   │     │ Socket  │ │
│  │   Broker    │          │  (Node.js)  │          │  (Database) │     │   IO    │ │
│  └──────┬──────┘          └──────┬──────┘          └─────────────┘     └────┬────┘ │
│         │                        │                                          │       │
│         │ MQTT                   │ Socket.IO                                │       │
│         │ subscribe              │ emit                                     │       │
│         ▼                        ▼                                          ▼       │
│  ┌─────────────┐          ┌─────────────┐                           ┌─────────────┐│
│  │ Simulators  │          │   Safety    │                           │    Web      ││
│  │ Stove/Fridge│          │   Logic     │                           │ Dashboard   ││
│  └─────────────┘          │ (Auto OFF)  │                           │ (Realtime)  ││
│                           └─────────────┘                           └─────────────┘│
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

# PHẦN 5: HƯỚNG DẪN CHẠY HỆ THỐNG

## 5.1. Yêu cầu môi trường

- Node.js >= 18.x
- MongoDB >= 6.x
- MQTT Broker (Mosquitto)
- PM2 (production)

## 5.2. Cài đặt và chạy

### Backend
```bash
cd back-end
npm install
# Tạo file .env với: PORT, JWT_SECRET, MQTT_HOST, MONGO_URI
npm start
```

### Simulators
```bash
cd front-end
npm install
node stove.js home/kitchen/stove1
node fridge.js home/kitchen/fridge1
```

### ESP32
- Mở Arduino IDE
- Cài thư viện: PubSubClient, UniversalTelegramBot, ArduinoJson
- Sửa WiFi/MQTT credentials trong 68.ino
- Upload lên ESP32

## 5.3. Truy cập
- Web Dashboard: http://localhost:3000
- Đăng ký tài khoản mới và bắt đầu sử dụng

---

# PHẦN 6: KẾT LUẬN

Hệ thống Smart Kitchen IoT được thiết kế với kiến trúc **event-driven**, sử dụng:

1. **MQTT** cho giao tiếp IoT (nhẹ, nhanh, phù hợp thiết bị nhúng)
2. **Socket.IO** cho realtime web updates (bi-directional)
3. **REST API** cho các thao tác CRUD (chuẩn, dễ mở rộng)
4. **FreeRTOS** cho ESP32 (đa nhiệm, phản hồi nhanh)

Hệ thống đảm bảo **an toàn** với các tính năng tự động:
- Tắt bếp khi phát hiện gas
- Đóng tủ lạnh khi nhiệt độ cao
- Cảnh báo Telegram tức thì

---

*Báo cáo được tạo tự động - Smart Kitchen IoT Project*
