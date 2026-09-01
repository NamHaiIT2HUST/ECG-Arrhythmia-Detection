# GIÁO TRÌNH FRONTEND CHO TRACK A
### (Dành riêng cho dự án ECG Arrhythmia Detection & XAI — CP3.6, CP4.1→4.5, CP5.5)

---

## LỜI MỞ ĐẦU: Vì sao giáo trình này được cấu trúc như thế này?

Tôi đã đọc kỹ `plan.md` và `pccv.md` của dự án bạn. Track A của bạn KHÔNG cần học toàn bộ "Frontend nói chung" — bạn cần một tập kỹ năng rất cụ thể, xếp theo đúng thứ tự bạn sẽ dùng:

| Việc bạn phải làm | Kiến thức cần | Phần trong giáo trình |
|:---|:---|:---:|
| CP3.6 — nối `StatCards`, `RecordSelector`, form upload | Fetch API, useState/useEffect, WebSocket trong React | Phần 5, 6 |
| CP4.1 — Patient UI, CRUD, localStorage | Context API, Form validation, localStorage | Phần 4, 8, 9 |
| CP4.2 — Alarm âm thanh + màu sắc | Web Audio API, Notification API | Phần 10, 11 |
| CP4.3 — Xuất PDF/CSV | jsPDF, html2canvas, Blob | Phần 12 |
| CP4.4 — XAI Explainer rút gọn | Chỉ là React thuần + Plotly (đã có sẵn) | Phần 3, 7 |
| CP4.5 — Settings, ngưỡng nhạy AI | localStorage, Context, `confidence` field | Phần 4, 8 |
| CP5.5 — Auth Guard | JWT flow, protected route pattern | Phần 13 |
| CP6.2 (phần Frontend) | Vitest, React Testing Library | Phần 14 |

Tôi sẽ dạy theo đúng thứ tự đó — mỗi phần có: **(a) khái niệm là gì, tại sao cần**, **(b) ví dụ tối giản để hiểu cơ chế**, **(c) ví dụ áp dụng thẳng vào code thật của dự án bạn** (dùng đúng tên file/biến trong `plan.md`).

Giả định: bạn đã biết HTML/CSS/JavaScript cơ bản, nhưng **chưa thạo React** và **chưa từng làm WebSocket/Canvas/PDF export**. Nếu bạn đã thạo React rồi, có thể nhảy thẳng tới Phần 5.

---

## PHẦN 0: CHUẨN BỊ MÔI TRƯỜNG

Trước khi học, hãy đảm bảo bạn chạy được dự án:

```bash
# Terminal 1 — chạy backend (đã có sẵn, không cần sửa gì ở CP3.6)
uvicorn backend.main:app --reload

# Terminal 2 — chạy frontend
cd frontend
npm install
npm run dev
```

Mở `http://localhost:5173` (Vite mặc định) — nếu thấy Dashboard đang chạy biểu đồ ECG là bạn đã sẵn sàng. Toàn bộ ví dụ trong giáo trình này bạn nên **tự gõ lại và chạy thử**, đừng chỉ đọc — React là môn học "tay làm mới nhớ".

---

## PHẦN 1: JAVASCRIPT HIỆN ĐẠI (ES6+) BẠN BẮT BUỘC PHẢI THẠO

React được viết bằng JavaScript hiện đại. Nếu chưa quen các cú pháp dưới đây, đọc code React sẽ như đọc mật mã. Đây là 7 cú pháp bạn sẽ gặp trong **mọi file** của dự án.

### 1.1. Arrow function (hàm mũi tên)

**Là gì**: một cách viết hàm ngắn gọn hơn `function`, và quan trọng hơn — nó **không tạo `this` riêng** (giữ nguyên `this` của ngữ cảnh bao quanh). Trong React, gần như 100% hàm bạn viết sẽ là arrow function.

```js
// Cách cũ
function tinhBPM(khoangRR) {
  return 60000 / khoangRR;
}

// Arrow function — tương đương
const tinhBPM = (khoangRR) => {
  return 60000 / khoangRR;
};

// Nếu chỉ có 1 dòng return, có thể bỏ luôn { return ... }
const tinhBPM = (khoangRR) => 60000 / khoangRR;

// Không có tham số
const noiXinChao = () => console.log("Xin chào");

// Nhiều tham số
const cong = (a, b) => a + b;
```

**Ứng dụng thật trong dự án** — bạn sẽ viết y hệt kiểu này trong `RecordSelector.jsx` (CP3.6):
```js
const handleChonBanGhi = (recordId) => {
  setSelectedRecord(recordId);   // đổi state
  // sau đó useEffect sẽ tự đóng WS cũ, mở WS mới (xem Phần 6)
};
```

### 1.2. Destructuring (tách biến từ object/array)

**Là gì**: thay vì viết `data.chunk`, `data.prediction`, `data.bpm`... nhiều lần, bạn "tách" thẳng các trường ra biến cùng tên.

```js
// Không dùng destructuring — dài dòng
const payload = { chunk: [1,2,3], prediction: "BÌNH THƯỜNG", bpm: 72 };
const chunk = payload.chunk;
const prediction = payload.prediction;
const bpm = payload.bpm;

// Dùng destructuring — 1 dòng, đọc rõ ràng luôn field nào đang được lấy ra
const { chunk, prediction, bpm } = payload;
```

**Ứng dụng thật** — payload WebSocket của dự án bạn (xem `plan.md` mục 2.3) có 8 trường: `chunk, prediction, heatmap, latency_ms, confidence, bpm, hrv_sdnn, hrv_rmssd, is_new_beat`. Khi nhận message ở CP3.6, bạn sẽ viết:

```js
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  const { chunk, prediction, heatmap, bpm, hrv_sdnn, hrv_rmssd, is_new_beat } = data;
  // giờ dùng thẳng bpm, hrv_sdnn... để cập nhật StatCards, không cần data.bpm nữa
};
```

Destructuring cũng dùng được với **props** của component (giải thích kỹ ở Phần 2) và với **array**:
```js
const [gia_tri_dau, gia_tri_hai] = [10, 20];  // destructuring array
const [count, setCount] = useState(0);         // đây chính là cú pháp bạn thấy ở useState!
```

### 1.3. Spread operator (`...`) — sao chép/gộp object, array

**Là gì**: dấu `...` "trải" nội dung của 1 object/array ra. Dùng nhiều nhất để **tạo bản sao mới** của state thay vì sửa trực tiếp (React yêu cầu điều này — giải thích ở Phần 3).

```js
const benhNhanCu = { id: "1", name: "Nguyễn Văn A", age: 60 };

// Tạo bản sao mới, chỉ đổi age — cách làm ĐÚNG trong React
const benhNhanMoi = { ...benhNhanCu, age: 61 };
// Kết quả: { id: "1", name: "Nguyễn Văn A", age: 61 }

// Với array — thêm 1 phần tử mới vào danh sách mà không sửa mảng gốc
const danhSachCu = [benhNhan1, benhNhan2];
const danhSachMoi = [...danhSachCu, benhNhan3];
```

**Ứng dụng thật** — CP4.1 (Patient Management), khi thêm 1 bệnh nhân mới vào `localStorage`:
```js
const themBenhNhan = (benhNhanMoi) => {
  setDanhSachBenhNhan((danhSachCu) => [...danhSachCu, benhNhanMoi]);
};
```

### 1.4. Optional chaining (`?.`) và Nullish coalescing (`??`)

**Là gì**: tránh lỗi "Cannot read property of undefined" — lỗi runtime phổ biến nhất khi làm việc với dữ liệu từ API (có thể chưa load xong, có thể null).

```js
// Nguy hiểm — nếu patient là null/undefined, dòng này crash cả app
const ten = patient.name;

// An toàn — nếu patient là null/undefined, ten sẽ là undefined, KHÔNG crash
const ten = patient?.name;

// Nullish coalescing — nếu vế trái là null/undefined, dùng giá trị mặc định bên phải
const ten = patient?.name ?? "Chưa có tên";
const bpm = data?.bpm ?? 0;
```

**Ứng dụng thật** — trong `StatCards.jsx` (CP3.6), lúc mới kết nối WS chưa có dữ liệu:
```jsx
<div className="stat-card">
  <span>BPM: {latestData?.bpm ?? "--"}</span>
  <span>HRV (SDNN): {latestData?.hrv_sdnn?.toFixed(1) ?? "--"} ms</span>
</div>
```

### 1.5. Template literals (chuỗi có biến bên trong)

```js
const recordId = "208";
// Cách cũ
const url = "ws://localhost:8000/ws/ecg?record=" + recordId;
// Template literal — dùng dấu backtick ` `, biến đặt trong ${...}
const url = `ws://localhost:8000/ws/ecg?record=${recordId}`;
```

Bạn sẽ dùng cú pháp này ở **mọi nơi** ghép URL trong CP3.6 và CP3.5 (form upload).

### 1.6. `async/await` — xử lý bất đồng bộ (gọi API)

**Là gì**: JavaScript chạy 1 luồng (single-threaded), nên các việc "tốn thời gian" như gọi API không thể chờ đồng bộ (sẽ đứng hình cả trang). `async/await` là cách viết code bất đồng bộ **trông giống code đồng bộ**, dễ đọc hơn nhiều so với cách cũ dùng `.then()`.

```js
// Hàm đánh dấu async thì mới được dùng await bên trong
async function layDanhSachBanGhi() {
  const response = await fetch("http://localhost:8000/api/records");
  const data = await response.json();  // chờ parse JSON xong
  return data;
}

// Gọi hàm async
layDanhSachBanGhi().then((data) => console.log(data));

// Hoặc trong 1 hàm async khác
async function main() {
  const data = await layDanhSachBanGhi();
  console.log(data);
}
```

**Xử lý lỗi với `try/catch`** — BẮT BUỘC phải có khi gọi API thật, vì server có thể lỗi, mạng có thể rớt:
```js
async function layDanhSachBanGhi() {
  try {
    const response = await fetch("http://localhost:8000/api/records");
    if (!response.ok) {
      throw new Error(`Lỗi server: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Không lấy được danh sách bản ghi:", error);
    return null;  // trả về giá trị an toàn thay vì để app crash
  }
}
```

**Ứng dụng thật** — chính xác đây là hàm bạn sẽ viết cho `RecordSelector.jsx` (CP3.6, xem `plan.md` mục 3.6).

### 1.7. Array methods: `.map()`, `.filter()`, `.find()`

React render danh sách (list of components) bằng `.map()` — bạn sẽ dùng liên tục cho: danh sách bệnh nhân (CP4.1), danh sách bản ghi (CP3.6), danh sách anomaly (CP4.4).

```js
const danhSachBenhNhan = [
  { id: "1", name: "Nguyễn Văn A", bedNumber: "101" },
  { id: "2", name: "Trần Thị B", bedNumber: "102" },
];

// .map() — biến đổi mỗi phần tử, thường dùng để render JSX
danhSachBenhNhan.map((bn) => bn.name);
// -> ["Nguyễn Văn A", "Trần Thị B"]

// .filter() — giữ lại phần tử thoả điều kiện
danhSachBenhNhan.filter((bn) => bn.bedNumber === "101");
// -> [{ id: "1", name: "Nguyễn Văn A", bedNumber: "101" }]

// .find() — tìm phần tử đầu tiên thoả điều kiện (hoặc undefined nếu không có)
danhSachBenhNhan.find((bn) => bn.id === "2");
// -> { id: "2", name: "Trần Thị B", bedNumber: "102" }
```

**Ứng dụng thật** — validate "bedNumber không trùng giữa các bệnh nhân đang active" (CP4.1, yêu cầu trong `plan.md` mục 4.2):
```js
const validateBedNumber = (bedNumberMoi, danhSachHienTai, idDangSua) => {
  const bịTrung = danhSachHienTai.some(
    (bn) => bn.bedNumber === bedNumberMoi && bn.id !== idDangSua
  );
  return !bịTrung;  // true nếu hợp lệ (không trùng)
};
```

---

## PHẦN 2: REACT CƠ BẢN — COMPONENT, JSX, PROPS

### 2.1. React là gì và tại sao dự án dùng nó

React là 1 thư viện JavaScript để xây UI bằng cách chia giao diện thành các **component** (khối tái sử dụng) — mỗi component tự quản lý trạng thái (state) của nó và **tự vẽ lại (re-render) khi state đổi**. Đây là lý do biểu đồ ECG của dự án bạn cập nhật mượt mà liên tục mà không cần bạn tự viết code "xoá canvas cũ, vẽ lại" — React tự làm việc đó.

Kiến trúc frontend dự án bạn (xem `plan.md` mục 2.4):
```
App.jsx (component gốc, quản lý tab đang chọn)
 ├── DashboardPage.jsx (component con — trang Theo Dõi Trực Tuyến)
 │    ├── ECGChart.jsx
 │    ├── StatCards.jsx
 │    └── EventLog.jsx
 ├── PatientPage.jsx (CP4.1 — bạn sẽ xây)
 └── SettingsPage.jsx (CP4.5 — bạn sẽ xây)
```

Mỗi thứ trong ngoặc vuông `.jsx` là **1 component** — về bản chất chỉ là 1 hàm JavaScript trả về JSX (giao diện).

### 2.2. JSX là gì

JSX là cú pháp cho phép viết "HTML" ngay trong JavaScript. Trình biên dịch (Vite/Babel) sẽ chuyển nó thành lời gọi hàm JavaScript thật.

```jsx
// Component đơn giản nhất — 1 hàm trả về JSX
function XinChao() {
  return <h1>Xin chào, đây là ECG Dashboard</h1>;
}
```

Quy tắc JSX cần nhớ:
- Phải trả về **đúng 1 phần tử gốc** (có thể bọc nhiều thứ trong `<div>` hoặc `<>...</>` — gọi là "Fragment").
- Nhúng biểu thức JavaScript bằng dấu ngoặc nhọn `{ }`.
- Thuộc tính HTML viết theo `camelCase`: `class` → `className`, `onclick` → `onClick`.

```jsx
function StatCards({ bpm, hrvSdnn }) {  // nhận props qua destructuring luôn trong tham số hàm
  const mauSac = bpm > 100 ? "do" : "xanh";  // biểu thức JS bình thường

  return (
    <div className="stat-cards">
      <div className={`card card-${mauSac}`}>
        <span>Nhịp tim: {bpm} bpm</span>
      </div>
      <div className="card">
        <span>HRV (SDNN): {hrvSdnn.toFixed(1)} ms</span>
      </div>
    </div>
  );
}
```

### 2.3. Props — cách component cha truyền dữ liệu cho component con

**Là gì**: Props (properties) giống như tham số hàm, nhưng dành cho component. Dữ liệu **chỉ chảy 1 chiều: từ cha xuống con** (đây là nguyên tắc cốt lõi của React, gọi là "one-way data flow" — hiểu nguyên tắc này giúp bạn không bao giờ bị rối khi debug tại sao UI không cập nhật).

```jsx
// Component con — nhận props
function PatientCard({ name, bedNumber, onClick }) {
  return (
    <div className="patient-card" onClick={onClick}>
      <h3>{name}</h3>
      <p>Giường: {bedNumber}</p>
    </div>
  );
}

// Component cha — truyền props xuống
function PatientPage() {
  const benhNhan = { name: "Nguyễn Văn A", bedNumber: "101" };

  const handleClick = () => {
    console.log("Đã bấm vào bệnh nhân:", benhNhan.name);
  };

  return (
    <PatientCard
      name={benhNhan.name}
      bedNumber={benhNhan.bedNumber}
      onClick={handleClick}
    />
  );
}
```

**Ứng dụng thật** — đây chính xác là cách bạn xây "Multi-bed Monitoring View" ở CP4.1: `PatientPage.jsx` (cha) chứa `danhSachBenhNhan`, dùng `.map()` để tạo nhiều `PatientCard` (con), mỗi card nhận `onClick` để khi bấm vào sẽ đổi bản ghi đang stream:

```jsx
function PatientPage() {
  const { danhSachBenhNhan, setActiveRecord } = usePatientContext(); // Context — học ở Phần 4

  return (
    <div className="patient-grid">
      {danhSachBenhNhan.map((bn) => (
        <PatientCard
          key={bn.id}                             // "key" — bắt buộc khi render list, xem lưu ý bên dưới
          name={bn.name}
          bedNumber={bn.bedNumber}
          onClick={() => setActiveRecord(bn.activeRecordId)}
        />
      ))}
    </div>
  );
}
```

**Lưu ý quan trọng về `key`**: khi dùng `.map()` để render 1 danh sách component, React **bắt buộc** mỗi phần tử phải có prop đặc biệt `key` (duy nhất, ổn định) để React biết phần tử nào là phần tử nào giữa các lần re-render — nếu thiếu, React sẽ cảnh báo trong console và có thể gây bug hiển thị sai khi danh sách thay đổi thứ tự. **Không dùng index của mảng làm `key`** nếu danh sách có thể bị thêm/xoá/sắp xếp lại (dùng `id` thật, như `bn.id` ở trên).

---

## PHẦN 3: REACT HOOKS CHUYÊN SÂU — `useState`, `useEffect`, `useRef`

Hooks là các hàm đặc biệt (luôn bắt đầu bằng `use`) cho phép component "có trí nhớ" (state) và "phản ứng với vòng đời" (effect) mà không cần viết class. Đây là phần **quan trọng nhất** của cả giáo trình — gần như mọi dòng code bạn viết ở CP3.6 và CP4 đều dùng 1 trong 3 hook này.

### 3.1. `useState` — lưu trạng thái của component

**Là gì**: biến "state" là dữ liệu mà khi thay đổi, React sẽ **tự động vẽ lại (re-render)** component đó. Khác với biến JavaScript thường (đổi giá trị không làm UI cập nhật), state là cách duy nhất để "báo" cho React biết "giao diện cần vẽ lại".

```jsx
import { useState } from "react";

function DemoCounter() {
  // useState(giá_trị_ban_đầu) trả về 1 CẶP: [giá trị hiện tại, hàm để đổi giá trị]
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Bạn đã bấm {count} lần</p>
      <button onClick={() => setCount(count + 1)}>Bấm vào đây</button>
    </div>
  );
}
```

Điều xảy ra khi bấm nút:
1. `setCount(count + 1)` được gọi.
2. React lưu giá trị `count` mới.
3. React **tự động gọi lại hàm `DemoCounter`** (re-render) với `count` đã cập nhật.
4. JSX trả về mới thay thế JSX cũ trên màn hình — nhưng React chỉ thực sự sửa đúng phần DOM đã đổi (gọi là "Virtual DOM diffing"), không vẽ lại toàn trang, nên rất nhanh.

**QUY TẮC CỰC KỲ QUAN TRỌNG**: **không bao giờ sửa trực tiếp state** (như `patients.push(...)` hay `patients[0].age = 61`) — luôn tạo **bản sao mới** rồi gọi hàm `set...`. Đây là lý do Phần 1.3 dạy bạn spread operator.

```jsx
// ❌ SAI — React không biết state đã đổi, UI không re-render đúng
const [patients, setPatients] = useState([]);
patients.push(benhNhanMoi);  // KHÔNG LÀM VẬY

// ✅ ĐÚNG — tạo mảng mới
setPatients([...patients, benhNhanMoi]);

// ✅ ĐÚNG với object — tạo object mới
const [settings, setSettings] = useState({ darkMode: false, wsUrl: "ws://localhost:8000" });
setSettings({ ...settings, darkMode: true });  // chỉ đổi darkMode, giữ nguyên wsUrl
```

**Ứng dụng thật** — `DashboardPage.jsx` (CP3.6) cần các state sau để lưu dữ liệu real-time:
```jsx
function DashboardPage() {
  const [selectedRecord, setSelectedRecord] = useState("208");  // bản ghi đang chọn
  const [xData, setXData] = useState([]);       // trục thời gian cho Plotly
  const [yData, setYData] = useState([]);       // giá trị tín hiệu ECG
  const [latestStats, setLatestStats] = useState({ bpm: 0, hrv_sdnn: 0, hrv_rmssd: 0 });
  const [heatmap, setHeatmap] = useState(null);
  // ...
}
```

**Dùng "hàm cập nhật" khi state mới phụ thuộc vào state cũ**: khi bạn cần thêm dữ liệu mới vào 1 mảng đang có (như thêm điểm mới vào biểu đồ ECG liên tục), cách an toàn nhất là truyền 1 **hàm** vào `setXData` thay vì giá trị:

```jsx
// Cách này có rủi ro nếu 2 lần gọi setYData xảy ra gần nhau (dùng giá trị yData "cũ" từ closure)
setYData([...yData, ...chunk]);

// Cách AN TOÀN — React đảm bảo "yDataCu" luôn là giá trị mới nhất tại thời điểm cập nhật
setYData((yDataCu) => {
  const yDataMoi = [...yDataCu, ...chunk];
  return yDataMoi.slice(-1000);  // chỉ giữ 1000 điểm gần nhất (đúng theo plan.md mục 2.4)
});
```

### 3.2. `useEffect` — chạy code khi component mount / khi 1 giá trị thay đổi / dọn dẹp khi unmount

**Là gì**: `useEffect` cho phép chạy "side effect" — những việc không thuộc về việc vẽ UI, như: gọi API, mở kết nối WebSocket, đăng ký sự kiện trình duyệt, hẹn giờ (`setTimeout`/`setInterval`).

Cấu trúc:
```jsx
useEffect(() => {
  // code chạy SAU khi component render xong

  return () => {
    // code "dọn dẹp" (cleanup) — chạy TRƯỚC lần effect tiếp theo, hoặc khi component bị gỡ bỏ
  };
}, [danhSachDependency]);  // effect chỉ chạy lại khi 1 trong các giá trị này thay đổi
```

**3 cách dùng mảng dependency — bắt buộc hiểu rõ, đây là nguồn bug số 1 của người mới học React:**

```jsx
// (a) Mảng RỖNG [] — effect chỉ chạy đúng 1 LẦN, ngay sau khi component xuất hiện lần đầu
useEffect(() => {
  console.log("Component vừa mount");
}, []);

// (b) KHÔNG có mảng dependency — effect chạy lại SAU MỌI LẦN render (hiếm khi cần, dễ gây vòng lặp vô hạn)
useEffect(() => {
  console.log("Chạy sau mọi lần render");
});

// (c) Mảng có giá trị — effect chạy lại MỖI KHI 1 trong các giá trị đó đổi
useEffect(() => {
  console.log("selectedRecord vừa đổi thành:", selectedRecord);
}, [selectedRecord]);
```

**Ứng dụng thật — đây chính là cơ chế bạn cần cho CP3.6** (đổi bản ghi → đóng WS cũ, mở WS mới, xem `plan.md` mục 3.6):

```jsx
useEffect(() => {
  // Mỗi khi selectedRecord đổi, effect này chạy lại:
  // React tự động chạy cleanup của lần TRƯỚC (đóng ws cũ) rồi mới chạy code mới (mở ws mới)
  const ws = new WebSocket(`ws://localhost:8000/ws/ecg?record=${selectedRecord}`);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    setYData((cu) => [...cu, ...data.chunk].slice(-1000));
    setLatestStats({ bpm: data.bpm, hrv_sdnn: data.hrv_sdnn, hrv_rmssd: data.hrv_rmssd });
  };

  ws.onerror = (err) => console.error("Lỗi WebSocket:", err);

  // Hàm cleanup — QUAN TRỌNG: nếu thiếu dòng này, mỗi lần đổi bản ghi sẽ mở thêm 1 kết nối WS
  // mới mà KHÔNG đóng kết nối cũ -> rò rỉ kết nối (memory leak), dashboard sẽ nhận trùng dữ liệu
  return () => {
    ws.close();
  };
}, [selectedRecord]);  // effect chạy lại mỗi khi selectedRecord (từ RecordSelector) đổi
```

Đây là lý do trong `plan.md` mục 3.6 có câu: *"sửa `DashboardPage.jsx`'s `connect()` để nhận `record` từ state thay vì hardcode"* — chính là đưa `selectedRecord` vào mảng dependency của `useEffect` như trên.

### 3.3. `useRef` — giữ 1 giá trị "sống sót" qua các lần render mà KHÔNG gây re-render

**Là gì**: khác với `useState` (đổi giá trị → re-render), `useRef` tạo ra 1 "hộp chứa" giá trị mà đổi nó **không** làm component vẽ lại. 2 công dụng chính:

**(a) Truy cập trực tiếp 1 phần tử DOM** (ví dụ cần cho `html2canvas` ở CP4.3 — chụp ảnh biểu đồ để xuất PDF):
```jsx
import { useRef } from "react";

function ECGChartWrapper() {
  const chartRef = useRef(null);  // khởi tạo rỗng

  const chupAnhBieuDo = async () => {
    // chartRef.current giờ CHÍNH LÀ phần tử DOM thật của div bên dưới
    const canvas = await html2canvas(chartRef.current);
    return canvas.toDataURL("image/png");
  };

  return (
    <div ref={chartRef}>  {/* gắn ref vào phần tử muốn truy cập */}
      <ECGChart />
    </div>
  );
}
```

**(b) Lưu giá trị không cần re-render** (ví dụ: đếm số lần retry kết nối WS, hoặc lưu ID của `setTimeout` để có thể huỷ sau):
```jsx
function useAutoReconnect(url) {
  const soLanThuLai = useRef(0);       // không cần hiển thị lên UI -> dùng ref, không dùng state
  const timeoutIdRef = useRef(null);

  const ketNoiLai = () => {
    soLanThuLai.current += 1;  // sửa .current KHÔNG gây re-render — khác hẳn setState
    timeoutIdRef.current = setTimeout(() => {
      console.log(`Đang thử kết nối lại lần ${soLanThuLai.current}...`);
    }, 3000);
  };
}
```

**Ứng dụng thật** — `plan.md` mục 2.4 nói `DashboardPage.jsx` có "auto-reconnect 3s" khi WS rớt. Đây là mẫu code chuẩn cho việc đó, kết hợp `useEffect` + `useRef`:

```jsx
useEffect(() => {
  let ws;
  let dangHuy = false;  // cờ để tránh reconnect sau khi component đã unmount

  const ketNoi = () => {
    ws = new WebSocket(`ws://localhost:8000/ws/ecg?record=${selectedRecord}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // ... cập nhật state như ở mục 3.2
    };

    ws.onclose = () => {
      if (!dangHuy) {
        setTimeout(ketNoi, 3000);  // tự kết nối lại sau 3 giây, đúng theo plan.md
      }
    };
  };

  ketNoi();

  return () => {
    dangHuy = true;
    ws.close();
  };
}, [selectedRecord]);
```

### 3.4. Custom Hook — đóng gói logic tái sử dụng

Khi 1 đoạn logic (state + effect) được dùng ở nhiều component, bạn "gói" nó thành 1 hàm bắt đầu bằng `use...`. Đây KHÔNG phải cú pháp đặc biệt của React — chỉ là quy ước đặt tên để React biết đó là hook (và cho phép hook đó gọi hook khác bên trong).

```jsx
// hooks/useLocalStorage.js — custom hook dùng cho CẢ CP4.1 (patients) và CP4.5 (settings)
import { useState, useEffect } from "react";

function useLocalStorage(key, giaTriMacDinh) {
  const [value, setValue] = useState(() => {
    // hàm khởi tạo "lazy" — chỉ chạy 1 LẦN lúc mount, không chạy lại mỗi lần render
    const daLuu = localStorage.getItem(key);
    return daLuu ? JSON.parse(daLuu) : giaTriMacDinh;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);  // mỗi khi value đổi, tự động lưu lại vào localStorage

  return [value, setValue];  // trả về y hệt kiểu useState — để dùng thay thế trực tiếp
}

export default useLocalStorage;
```

Dùng trong CP4.1:
```jsx
function PatientPage() {
  // dùng y hệt useState, nhưng giờ tự động lưu vào localStorage key "ecg_patients"
  const [patients, setPatients] = useLocalStorage("ecg_patients", []);
  // ...
}
```

Dùng trong CP4.5:
```jsx
function SettingsPage() {
  const [settings, setSettings] = useLocalStorage("ecg_settings", {
    wsUrl: "ws://localhost:8000",
    darkMode: false,
    sensitivityThreshold: 0.7,
  });
  // ...
}
```

Đây chính là cách bạn tránh viết lặp lại logic `localStorage.getItem/setItem` ở cả `PatientContext.jsx` và `SettingsPage.jsx`.

---

## PHẦN 4: CONTEXT API — QUẢN LÝ STATE TOÀN CỤC

### 4.1. Vấn đề Context giải quyết: "Prop Drilling"

Giả sử `App.jsx` có dữ liệu `patients`, nhưng component cần dùng nó lại nằm sâu bên trong: `App` → `PatientPage` → `PatientGrid` → `PatientCard`. Nếu truyền qua props thông thường, bạn phải truyền `patients` qua **từng tầng trung gian** dù bản thân `PatientPage`/`PatientGrid` không cần dùng nó — gọi là "prop drilling", code rất khó bảo trì.

**Context** giải quyết bằng cách tạo ra 1 "kho dữ liệu toàn cục" mà **bất kỳ component con nào** (dù ở tầng sâu bao nhiêu) cũng lấy được trực tiếp, không cần truyền qua từng tầng.

Dự án bạn đã có sẵn ví dụ: `AnomalyContext.jsx` (xem `plan.md` mục 2.4) — lưu lịch sử 20 nhịp lỗi gần nhất, dùng chung giữa `DashboardPage` và `XAIPage`. Bạn sẽ viết thêm 2 Context mới theo đúng pattern này: `PatientContext.jsx` (CP4.1) và `AuthContext.jsx` (CP5.5).

### 4.2. Cách tạo 1 Context — 3 bước chuẩn

**Bước 1 — Tạo Context và Provider** (`context/PatientContext.jsx`):
```jsx
import { createContext, useContext, useState, useEffect } from "react";

// Bước 1a: tạo "kho chứa" — ban đầu rỗng, sẽ được Provider cấp giá trị thật
const PatientContext = createContext(null);

// Bước 1b: Provider — component "bọc" quanh phần app cần dùng chung dữ liệu này
export function PatientProvider({ children }) {
  const [patients, setPatients] = useState(() => {
    const daLuu = localStorage.getItem("ecg_patients");
    return daLuu ? JSON.parse(daLuu) : [];
  });

  useEffect(() => {
    localStorage.setItem("ecg_patients", JSON.stringify(patients));
  }, [patients]);

  const themBenhNhan = (benhNhanMoi) => {
    setPatients((cu) => [...cu, { ...benhNhanMoi, id: crypto.randomUUID() }]);
  };

  const suaBenhNhan = (id, duLieuMoi) => {
    setPatients((cu) => cu.map((bn) => (bn.id === id ? { ...bn, ...duLieuMoi } : bn)));
  };

  const xoaBenhNhan = (id) => {
    setPatients((cu) => cu.filter((bn) => bn.id !== id));
  };

  // "value" là TẤT CẢ những gì component con có thể lấy ra được từ Context này
  const value = { patients, themBenhNhan, suaBenhNhan, xoaBenhNhan };

  return <PatientContext.Provider value={value}>{children}</PatientContext.Provider>;
}

// Bước 1c: custom hook tiện dùng — thay vì phải gọi useContext(PatientContext) mọi nơi
export function usePatientContext() {
  const context = useContext(PatientContext);
  if (!context) {
    throw new Error("usePatientContext phải được gọi bên trong PatientProvider");
  }
  return context;
}
```

**Bước 2 — Bọc `PatientProvider` quanh phần app cần dùng** (`App.jsx` hoặc `main.jsx`):
```jsx
import { PatientProvider } from "./context/PatientContext";

function App() {
  return (
    <PatientProvider>
      {/* mọi component bên trong đây đều gọi được usePatientContext() */}
      <Header />
      <PatientPage />
      <DashboardPage />
    </PatientProvider>
  );
}
```

**Bước 3 — Dùng ở bất kỳ component con nào**, dù sâu tới đâu, KHÔNG cần truyền props qua trung gian:
```jsx
function PatientCard({ patientId }) {
  const { patients, xoaBenhNhan } = usePatientContext();  // lấy trực tiếp, không qua props!
  const benhNhan = patients.find((bn) => bn.id === patientId);

  return (
    <div className="patient-card">
      <h3>{benhNhan.name}</h3>
      <button onClick={() => xoaBenhNhan(benhNhan.id)}>Xoá</button>
    </div>
  );
}
```

### 4.3. Khi nào dùng Context, khi nào dùng `useState` cục bộ?

Quy tắc thực dụng (không phải lý thuyết hàn lâm):
- **Dùng `useState` cục bộ** nếu dữ liệu chỉ 1 component cần (ví dụ: giá trị đang gõ trong 1 ô input của form, trạng thái "modal đang mở/đóng").
- **Dùng Context** nếu ≥ 2 component không liên quan trực tiếp (không phải cha-con trực tiếp) đều cần đọc/sửa cùng 1 dữ liệu. Trong dự án bạn: `patients` (CP4.1), `settings` (CP4.5), `authState` (CP5.5), `anomalyHistory` (đã có sẵn) đều xứng đáng là Context vì được dùng ở nhiều trang khác nhau.

### 4.4. Ví dụ thứ 2 để củng cố: `AuthContext` cho CP5.5

Đây là bản rút gọn (bản đầy đủ có thêm refresh-token logic ở Phần 13):
```jsx
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);          // { id, username, role } hoặc null nếu chưa login
  const [token, setToken] = useState(() => localStorage.getItem("access_token"));

  const dangNhap = async (username, password) => {
    const res = await fetch("http://localhost:8000/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) throw new Error("Sai tài khoản hoặc mật khẩu");
    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    setToken(data.access_token);
    setUser({ username, role: data.role });
  };

  const dangXuat = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, dangNhap, dangXuat }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
```

---

## PHẦN 5: GIAO TIẾP MẠNG — FETCH API (Gọi REST API từ React)

### 5.1. Fetch API cơ bản — nhắc lại có kèm giải thích sâu hơn về GET/POST

Dự án bạn có 3 REST endpoint cần gọi ở CP3.6 (xem `plan.md` mục 3.4): `GET /api/records`, `POST /api/diagnosis/upload-ecg`, và sau này `POST /api/auth/login` (CP5.5), `GET /api/anomalies` (nếu Track A cần đọc lịch sử).

**GET — lấy dữ liệu, không có body**:
```js
async function layDanhSachBanGhi() {
  const response = await fetch("http://localhost:8000/api/records");
  if (!response.ok) throw new Error(`Lỗi ${response.status}`);
  return await response.json();
  // Kết quả đúng theo plan.md mục 3.4:
  // { default_record: "208", count: 48, records: [{ id, description, is_default }, ...] }
}
```

**POST — gửi dữ liệu JSON lên server** (dùng cho login):
```js
async function dangNhap(username, password) {
  const response = await fetch("http://localhost:8000/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },  // báo cho server biết body là JSON
    body: JSON.stringify({ username, password }),       // PHẢI chuyển object thành chuỗi JSON
  });
  return await response.json();
}
```

**POST với `FormData` — dùng khi upload FILE** (khác hẳn JSON, dùng cho form upload CSV ở CP3.6):
```js
async function chanDoanOffline(file) {
  const formData = new FormData();
  formData.append("file", file);  // "file" phải khớp tên field backend mong đợi

  const response = await fetch("http://localhost:8000/api/diagnosis/upload-ecg?fs=360", {
    method: "POST",
    body: formData,
    // LƯU Ý: KHÔNG set header "Content-Type" thủ công khi dùng FormData —
    // trình duyệt tự thêm đúng "multipart/form-data; boundary=..." — nếu bạn tự set sẽ SAI và lỗi
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Chẩn đoán thất bại");
  }
  return await response.json();
  // Kết quả đúng theo plan.md mục 3.4:
  // { total_beats, duration_seconds, class_counts, bpm, hrv, anomalies, overall_assessment, ... }
}
```

### 5.2. Kết hợp Fetch với `useState` + `useEffect` — pattern chuẩn để "gọi API khi component mount"

Đây là pattern bạn sẽ viết cho `RecordSelector.jsx` (CP3.6, yêu cầu "gọi `GET /api/records` lúc mount"):

```jsx
function RecordSelector({ selectedRecord, onChangeRecord }) {
  const [records, setRecords] = useState([]);
  const [dangTai, setDangTai] = useState(true);
  const [loi, setLoi] = useState(null);

  useEffect(() => {
    async function taiDanhSach() {
      try {
        setDangTai(true);
        const response = await fetch("http://localhost:8000/api/records");
        if (!response.ok) throw new Error(`Lỗi ${response.status}`);
        const data = await response.json();
        setRecords(data.records);
      } catch (err) {
        setLoi(err.message);
      } finally {
        setDangTai(false);
      }
    }
    taiDanhSach();
  }, []);  // [] rỗng -> chỉ gọi API 1 LẦN lúc component vừa xuất hiện

  if (dangTai) return <p>Đang tải danh sách bản ghi...</p>;
  if (loi) return <p>Lỗi: {loi}</p>;

  return (
    <select
      value={selectedRecord}
      onChange={(e) => onChangeRecord(e.target.value)}  // gọi callback từ props cha (DashboardPage)
    >
      {records.map((rec) => (
        <option key={rec.id} value={rec.id}>
          {rec.id} — {rec.description}
        </option>
      ))}
    </select>
  );
}
```

Ba biến state `dangTai`/`loi`/dữ liệu là **bộ ba kinh điển** khi gọi API trong React — luôn xử lý đủ 3 trạng thái: đang tải / lỗi / có dữ liệu. Bỏ qua bước này là nguyên nhân phổ biến khiến UI "trắng trang" hoặc crash khi mạng chậm.

---

## PHẦN 6: WEBSOCKET TRONG REACT (Trái tim của Dashboard real-time)

### 6.1. WebSocket khác Fetch API ở điểm nào

- **Fetch (HTTP)**: mô hình "hỏi 1 câu, nhận 1 câu trả lời", rồi kết nối đóng lại. Phù hợp lấy danh sách bản ghi, gửi form.
- **WebSocket**: mở **1 kết nối duy trì liên tục** 2 chiều — server có thể **tự động đẩy (push)** dữ liệu về client bất cứ lúc nào mà không cần client hỏi lại. Đây là lý do dự án dùng WebSocket cho luồng ECG real-time: backend liên tục gửi từng gói 10 điểm tín hiệu/36 lần mỗi giây (xem `plan.md` mục 2.2), Fetch không làm được việc này hiệu quả.

### 6.2. API `WebSocket` gốc của trình duyệt (không cần thư viện ngoài)

```js
const ws = new WebSocket("ws://localhost:8000/ws/ecg?record=208");

ws.onopen = () => {
  console.log("Đã kết nối WebSocket");
};

ws.onmessage = (event) => {
  // event.data LUÔN là chuỗi (string) — phải tự parse JSON
  const data = JSON.parse(event.data);
  console.log("Nhận gói tin:", data);
};

ws.onerror = (error) => {
  console.error("Lỗi WebSocket:", error);
};

ws.onclose = (event) => {
  console.log("Kết nối đã đóng, code:", event.code);
};

// Đóng kết nối chủ động (BẮT BUỘC gọi khi không cần nữa, ví dụ khi đổi bản ghi hoặc rời trang)
ws.close();
```

### 6.3. Tại sao PHẢI đóng WebSocket trong cleanup của `useEffect`

Đây là lỗi phổ biến nhất khi làm CP3.6. Nếu bạn quên `return () => ws.close()`:

```
Lần 1: user chọn record "100" -> mở WS #1 -> nhận data từ record 100
Lần 2: user chọn record "208" -> mở WS #2 -> NHƯNG WS #1 VẪN CÒN MỞ
      -> component nhận dữ liệu TRỘN LẪN từ cả 2 kết nối cùng lúc
      -> biểu đồ ECG hiển thị lởm chởm/sai hoàn toàn
      -> sau vài lần đổi record, có thể có 5-10 kết nối WS mở song song
      -> tốn tài nguyên cả client lẫn server, cuối cùng server treo
```

Đoạn code đầy đủ, đúng (nhắc lại từ Phần 3.2, giờ giải thích rõ TẠI SAO từng dòng cần thiết):

```jsx
useEffect(() => {
  const ws = new WebSocket(`ws://localhost:8000/ws/ecg?record=${selectedRecord}`);
  let dangHuy = false;

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    const { chunk, prediction, heatmap, bpm, hrv_sdnn, hrv_rmssd, is_new_beat, confidence } = data;

    setYData((cu) => [...cu, ...chunk].slice(-1000));   // giữ 1000 điểm gần nhất, đúng plan.md mục 2.4
    setXData((cu) => {
      const tsBatDau = cu.length > 0 ? cu[cu.length - 1] + 1 : 0;
      const tsMoi = chunk.map((_, i) => tsBatDau + i);
      return [...cu, ...tsMoi].slice(-1000);
    });
    setLatestStats({ bpm, hrv_sdnn, hrv_rmssd, confidence, prediction });

    if (heatmap !== null) {
      setHeatmap(heatmap);       // chỉ khác null đúng lúc có nhịp bất thường mới (xem plan.md mục 2.3)
    }
  };

  ws.onclose = () => {
    if (!dangHuy) setTimeout(() => { /* logic reconnect, xem Phần 3.3 */ }, 3000);
  };

  return () => {
    dangHuy = true;
    ws.close();   // <<< DÒNG QUAN TRỌNG NHẤT CỦA TOÀN BỘ CP3.6
  };
}, [selectedRecord]);
```

### 6.4. Sample-and-hold — hiểu đúng ngữ nghĩa payload để không code sai

`plan.md` mục 3.4/2.3 giải thích: `prediction`, `bpm`, `hrv_sdnn`, `hrv_rmssd` dùng cơ chế **"sample-and-hold"** — nghĩa là giá trị này **giữ nguyên giữa 2 nhịp tim** (chỉ đổi đúng lúc có 1 nhịp mới được chẩn đoán), NHƯNG `heatmap` là ngoại lệ: nó là `null` ở hầu hết gói tin, và **chỉ khác `null` đúng ở gói tin vừa có 1 nhịp bất thường mới**.

Điều này quan trọng vì nếu bạn code `setHeatmap(data.heatmap)` KHÔNG kiểm tra `!== null`, mỗi gói tin (36 lần/giây) sẽ liên tục ghi đè `heatmap` bằng `null`, và `XAIPage`/highlight đỏ trên `ECGChart` sẽ **chớp tắt liên tục** thay vì giữ ổn định đúng như thiết kế. Đây chính xác là lý do đoạn code Phần 6.3 có `if (heatmap !== null)`.

### 6.5. Test thủ công CP3.6 — theo đúng DoD trong `pccv.md`

`pccv.md` mục A1 ghi rõ cách test: *"đổi bản ghi qua `100` (bình thường) và `208` (nhiều PVC), xác nhận số liệu đổi đúng"*. Quy trình cụ thể:
1. Chạy cả backend (`uvicorn backend.main:app`) và frontend (`npm run dev`).
2. Mở tab DevTools → Network → lọc "WS" để thấy các gói tin JSON đang chảy qua — kiểm tra `bpm`/`hrv_sdnn` có giá trị hợp lý (không phải `NaN`/`undefined`).
3. Đổi bản ghi từ `RecordSelector` sang `100` → xác nhận BPM ổn định, gần như không có cảnh báo đỏ (nhịp bình thường).
4. Đổi sang `208` → xác nhận nhiều cảnh báo PVC xuất hiện (đúng mô tả "Ngoại tâm thu thất tần suất rất cao" trong `plan.md` mục 3.4).
5. Kiểm tra Network tab: đổi record 5 lần liên tiếp, xác nhận **chỉ có 1 kết nối WS đang mở tại 1 thời điểm** (không tích luỹ nhiều kết nối "Pending"/"101 Switching Protocols" cùng lúc) — đây chính là cách phát hiện lỗi ở mục 6.3 nếu bạn quên cleanup.

---

## PHẦN 7: TRỰC QUAN HOÁ DỮ LIỆU VỚI PLOTLY.JS

Dự án đã dùng Plotly (`plan.md` mục 2.4: "React Plotly Streaming Dashboard") cho cả `ECGChart.jsx` và biểu đồ Bar+Line ở `XAIPage.jsx`. Ở CP4.4, bạn cần **thêm chú thích rõ ràng** vào biểu đồ đã có sẵn (không cần build lại từ đầu) — nên phần này tập trung vào phần bạn thực sự cần: đọc hiểu và chỉnh sửa cấu hình Plotly có sẵn.

### 7.1. Cấu trúc cơ bản của `react-plotly.js`

```jsx
import Plot from "react-plotly.js";

function ECGChart({ xData, yData, heatmap, isDanger }) {
  return (
    <Plot
      data={[
        {
          x: xData,
          y: yData,
          type: "scatter",
          mode: "lines",
          line: { color: "#00cc44", width: 1.5 },
          name: "Tín hiệu ECG",
        },
      ]}
      layout={{
        title: "Điện tâm đồ thời gian thực",
        xaxis: { title: "Thời gian (mẫu)" },
        yaxis: { title: "Biên độ" },
        shapes: isDanger
          ? [
              {
                // Đây chính là "dải shapes rect" mà plan.md mục 4.5 nhắc tới cho vùng highlight đỏ
                type: "rect",
                x0: xData[xData.length - 187],  // 187 điểm gần nhất = 1 nhịp vừa chẩn đoán
                x1: xData[xData.length - 1],
                y0: Math.min(...yData),
                y1: Math.max(...yData),
                fillcolor: "rgba(255,0,0,0.2)",
                line: { width: 0 },
              },
            ]
          : [],
      }}
      config={{ responsive: true }}
    />
  );
}
```

Điểm cần hiểu: `data` là **mảng các "trace"** (mỗi trace là 1 đường/1 tập điểm vẽ trên cùng biểu đồ), `layout` cấu hình tiêu đề/trục/chú thích/hình vẽ phụ (`shapes`), `config` cấu hình hành vi tương tác (zoom, responsive...).

### 7.2. Biểu đồ Bar+Line kết hợp cho `XAIPage.jsx` (heatmap Grad-CAM đè lên sóng ECG)

`plan.md` mục 2.4 mô tả: *"Plotly Bar+Line kết hợp (heatmap đè lên sóng ECG)"*. Đây là cách vẽ 2 loại trace khác nhau trên cùng 1 biểu đồ, dùng chung 1 trục X:

```jsx
function XAIHeatmapChart({ beatSignal, heatmapValues }) {
  // beatSignal: 187 điểm tín hiệu của 1 nhịp
  // heatmapValues: 187 điểm cường độ Grad-CAM (0-1), model chú ý vùng nào nhất

  return (
    <Plot
      data={[
        {
          x: Array.from({ length: 187 }, (_, i) => i),
          y: heatmapValues,
          type: "bar",
          marker: { color: heatmapValues, colorscale: "Reds" },  // đậm hơn = model chú ý nhiều hơn
          name: "Grad-CAM (mức độ chú ý của AI)",
          opacity: 0.5,
          yaxis: "y2",  // dùng trục Y phụ, để scale khác với sóng ECG
        },
        {
          x: Array.from({ length: 187 }, (_, i) => i),
          y: beatSignal,
          type: "scatter",
          mode: "lines",
          line: { color: "#0066cc" },
          name: "Sóng ECG",
        },
      ]}
      layout={{
        title: "Vùng AI tập trung chú ý nhất",  // đúng chú thích yêu cầu ở CP4.4
        yaxis: { title: "Biên độ tín hiệu" },
        yaxis2: { title: "Mức độ chú ý", overlaying: "y", side: "right", range: [0, 1] },
      }}
    />
  );
}
```

### 7.3. CP4.4 thực chất bạn cần làm gì (nhắc lại phạm vi từ `plan.md` mục 4.5)

Component biểu đồ **đã có sẵn** — CP4.4 chỉ cần:
1. Tạo file tra cứu tĩnh `frontend/src/constants/clinicalExplanations.js` — 1 object JS ánh xạ nhãn → mô tả:
```js
export const clinicalExplanations = {
  "BÌNH THƯỜNG": "Nhịp xoang bình thường, không phát hiện bất thường về hình dạng phức bộ QRS.",
  "CẢNH BÁO: TRÊN THẤT (S)": "Ngoại tâm thu nhĩ/trên thất — phức bộ QRS hẹp nhưng đến sớm hơn dự kiến, thường có sóng P bất thường hoặc không rõ đi trước.",
  "CẢNH BÁO: NHỊP THẤT (V)": "Ngoại tâm thu thất — phức bộ QRS thường dãn rộng >120ms, không có sóng P đi trước, hình dạng khác biệt rõ so với nhịp bình thường.",
  "CẢNH BÁO: HỢP NHẤT (F)": "Nhịp hợp nhất — kết hợp đặc điểm của cả nhịp bình thường và nhịp thất, hình dạng trung gian giữa 2 loại.",
  "CẢNH BÁO: CHƯA RÕ (Q)": "Nhịp không phân loại rõ ràng — cần bác sĩ xem xét kỹ tín hiệu gốc để chẩn đoán chính xác.",
};
```
2. Ở `XAIPage.jsx`, khi user chọn 1 nhịp bất thường trong lịch sử, hiển thị `clinicalExplanations[nhipDangChon.prediction]` bên cạnh biểu đồ đã có.
3. Đảm bảo phần chú thích ("vùng AI tập trung chú ý nhất") xuất hiện rõ ràng cạnh biểu đồ heatmap ở mục 7.2.

**Không** làm thêm việc đo PR/QRS/ST bằng mili-giây — `plan.md` nói rõ đây là "1 bài toán DSP lớn... không nằm trong phạm vi CP4".

---

## PHẦN 8: LOCALSTORAGE — LƯU TRỮ PHÍA CLIENT

### 8.1. `localStorage` là gì, giới hạn của nó

`localStorage` là 1 kho lưu trữ key-value **có sẵn trong trình duyệt**, tồn tại **vĩnh viễn** cho tới khi bị xoá thủ công (khác với biến JS thường, mất khi F5). Đây là lý do `plan.md` mục 4.1 chọn nó làm nơi lưu tạm bệnh nhân/settings ở CP4, tránh phải chờ database (CP5).

Giới hạn cần biết:
- Chỉ lưu được **chuỗi (string)** — object/array phải `JSON.stringify()` trước khi lưu, và `JSON.parse()` khi đọc ra.
- Giới hạn dung lượng ~5-10MB tuỳ trình duyệt (đủ dùng cho danh sách bệnh nhân, không đủ cho lưu file lớn).
- Dữ liệu **chỉ tồn tại trên máy/trình duyệt hiện tại** — không tự đồng bộ giữa các máy khác nhau (đây chính xác là lý do `plan.md` mục 5.1 liệt kê nó là "hạn chế" cần CP5/database giải quyết sau này).

### 8.2. API cơ bản

```js
// Lưu (object/array phải stringify trước)
localStorage.setItem("ecg_patients", JSON.stringify(danhSachBenhNhan));

// Đọc (phải parse lại, và LUÔN kiểm tra null vì lần đầu chạy sẽ chưa có gì)
const daLuu = localStorage.getItem("ecg_patients");
const danhSach = daLuu ? JSON.parse(daLuu) : [];

// Xoá 1 key
localStorage.removeItem("ecg_patients");

// Xoá tất cả (cẩn thận — xoá luôn cả token đăng nhập nếu có)
localStorage.clear();
```

### 8.3. 2 key chính xác dự án bạn cần dùng (đúng tên trong `plan.md`/`pccv.md` — GIỮ NGUYÊN TÊN vì Track B sẽ dựa vào đây để viết script di cư dữ liệu sau này)

| Key | Dùng ở | Cấu trúc dữ liệu |
|:---|:---|:---|
| `ecg_patients` | CP4.1 | mảng object bệnh nhân (xem cấu trúc đầy đủ ở `plan.md` mục 4.2) |
| `ecg_settings` | CP4.5 | object 1 cấp (`wsUrl`, `darkMode`, `sensitivityThreshold`, ...) |
| `access_token`, `refresh_token` | CP5.5 | chuỗi JWT (KHÔNG phải object, không cần `JSON.stringify`) |

**Lưu ý quan trọng từ `pccv.md` mục A2**: khi báo cáo hoàn thành CP4.1, bạn phải **ghi rõ tên key `ecg_patients`** trong tin nhắn báo — vì Track B sẽ cần đúng tên này để viết script di cư dữ liệu sang database thật ở giai đoạn sau. Đừng tự đổi tên key nếu không báo trước.

### 8.4. Bẫy thường gặp: đồng bộ `localStorage` với `useState`

```jsx
// ❌ SAI — chỉ đọc localStorage 1 lần lúc khởi tạo, nhưng KHÔNG tự lưu lại khi state đổi
const [patients, setPatients] = useState(JSON.parse(localStorage.getItem("ecg_patients") || "[]"));
setPatients([...patients, benhNhanMoi]);  // state đổi trong React, nhưng localStorage KHÔNG đổi theo
// -> F5 lại, dữ liệu mới mất — sai DoD "dữ liệu còn sau F5" của CP4.1

// ✅ ĐÚNG — dùng useEffect để TỰ ĐỘNG lưu lại mỗi khi patients đổi (xem custom hook ở Phần 3.4)
useEffect(() => {
  localStorage.setItem("ecg_patients", JSON.stringify(patients));
}, [patients]);
```

---

## PHẦN 9: FORM & VALIDATION TRONG REACT

### 9.1. Controlled input — cách React "kiểm soát" giá trị ô input

Trong React, thay vì để trình duyệt tự quản lý giá trị input (uncontrolled), ta thường cho **React state là nguồn sự thật duy nhất** — gọi là "controlled component". Mỗi lần gõ phím, `onChange` cập nhật state, và `value` của input luôn phản ánh đúng state đó.

```jsx
function PatientForm({ onSubmit }) {
  const [form, setForm] = useState({
    name: "", age: "", gender: "M", bedNumber: "", admissionDate: "", diagnosis: "",
    attendingDoctor: "",
  });
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;   // destructuring trực tiếp từ sự kiện input
    setForm((cu) => ({ ...cu, [name]: value }));  // "computed property name" — dùng [name] để đổi ĐÚNG field đang gõ
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); /* xử lý submit, xem 9.2 */ }}>
      <input name="name" value={form.name} onChange={handleChange} placeholder="Họ tên" />
      {errors.name && <span className="error">{errors.name}</span>}

      <input name="age" type="number" value={form.age} onChange={handleChange} placeholder="Tuổi" />
      {errors.age && <span className="error">{errors.age}</span>}

      <button type="submit">Lưu</button>
    </form>
  );
}
```

Giải thích `[name]: value` (computed property name) — đây là cách viết "tên field trong ngoặc vuông" để dùng **giá trị của biến `name`** làm tên thuộc tính, thay vì viết cứng từng field:
```js
// Nếu KHÔNG dùng computed property name, bạn phải viết 7 hàm riêng cho 7 field:
const handleChangeName = (e) => setForm({ ...form, name: e.target.value });
const handleChangeAge = (e) => setForm({ ...form, age: e.target.value });
// ... rất dài dòng

// Với computed property name — 1 HÀM DUY NHẤT xử lý mọi field, vì input nào cũng có "name" attribute HTML khớp với tên field
const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
```

### 9.2. Validate dữ liệu trước khi submit — đúng yêu cầu CP4.1

`plan.md` mục 4.2 yêu cầu: `name` bắt buộc, `age` 0-120, `bedNumber` không trùng giữa bệnh nhân đang active.

```jsx
function validate(form, danhSachHienTai, idDangSua) {
  const errors = {};

  if (!form.name.trim()) {
    errors.name = "Họ tên là bắt buộc";
  }

  const age = Number(form.age);
  if (Number.isNaN(age) || age < 0 || age > 120) {
    errors.age = "Tuổi phải trong khoảng 0-120";
  }

  const trungGiuong = danhSachHienTai.some(
    (bn) => bn.bedNumber === form.bedNumber && bn.id !== idDangSua
  );
  if (trungGiuong) {
    errors.bedNumber = "Số giường này đã có bệnh nhân khác đang dùng";
  }

  return errors;  // object rỗng {} nghĩa là hợp lệ, có key nghĩa là có lỗi
}

function PatientForm({ onSubmit, danhSachHienTai, benhNhanDangSua }) {
  const [form, setForm] = useState(benhNhanDangSua ?? { name: "", age: "", bedNumber: "" /* ... */ });
  const [errors, setErrors] = useState({});

  const handleSubmit = (e) => {
    e.preventDefault();  // ngăn form tự reload trang (hành vi mặc định của HTML form)
    const loi = validate(form, danhSachHienTai, benhNhanDangSua?.id);
    if (Object.keys(loi).length > 0) {   // Object.keys() đếm số field bị lỗi
      setErrors(loi);
      return;  // dừng lại, không submit
    }
    setErrors({});
    onSubmit(form);  // gọi callback từ component cha (thường là themBenhNhan/suaBenhNhan từ Context)
  };

  return <form onSubmit={handleSubmit}>{/* ...các input như 9.1... */}</form>;
}
```

### 9.3. Select (dropdown) cho `gender`

```jsx
<select name="gender" value={form.gender} onChange={handleChange}>
  <option value="M">Nam</option>
  <option value="F">Nữ</option>
  <option value="Other">Khác</option>
</select>
```

---

## PHẦN 10: WEB AUDIO API — TẠO ÂM THANH CẢNH BÁO (CP4.2)

### 10.1. Vì sao dùng `OscillatorNode` thay vì file mp3

`plan.md` mục 4.3 chỉ định rõ: *"dùng `OscillatorNode` (Web Audio API, không cần file mp3)"*. Lý do thực tế: `OscillatorNode` tạo âm thanh **bằng code** (tần số, dạng sóng) — không cần tải file audio, dễ điều chỉnh nhịp beep chính xác theo chuẩn y tế IEC 60601-1-8, và nhẹ hơn nhiều so với nhúng file mp3.

### 10.2. Web Audio API cơ bản — phát 1 tiếng "beep"

```js
function phatBeep(tanSo = 880, thoiLuongMs = 150) {
  // AudioContext là "công xưởng âm thanh" của trình duyệt — chỉ nên tạo 1 lần, dùng lại nhiều lần
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

  const oscillator = audioCtx.createOscillator();  // nguồn phát sóng âm
  const gainNode = audioCtx.createGain();           // điều chỉnh âm lượng (để beep không "bụp" gắt)

  oscillator.type = "sine";              // dạng sóng: sine (êm), square (chói hơn, giống báo động y tế thật)
  oscillator.frequency.value = tanSo;    // đơn vị Hz — càng cao càng "chói"

  oscillator.connect(gainNode);
  gainNode.connect(audioCtx.destination);  // "destination" = loa của máy

  gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);  // âm lượng 30%, tránh giật mình người nghe

  oscillator.start();
  oscillator.stop(audioCtx.currentTime + thoiLuongMs / 1000);  // tự dừng sau X mili-giây
}
```

### 10.3. Xây `alarmAudio.js` theo đúng chuẩn IEC 60601-1-8 (yêu cầu trong `plan.md` mục 4.3)

Chuẩn này quy định: **mức 2 (Chú ý)** = 1 beep/giây; **mức 3 (Khẩn cấp)** = cụm 3 beep liên tiếp mỗi 2 giây. Đây là cách hiện thực bằng `setInterval` kết hợp hàm phát beep ở trên:

```js
// utils/alarmAudio.js
let audioCtx = null;
let intervalId = null;

function getAudioContext() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  return audioCtx;
}

function phatMotBeep(tanSo, thoiLuongMs) {
  const ctx = getAudioContext();
  const oscillator = ctx.createOscillator();
  const gainNode = ctx.createGain();
  oscillator.type = "square";
  oscillator.frequency.value = tanSo;
  oscillator.connect(gainNode);
  gainNode.connect(ctx.destination);
  gainNode.gain.setValueAtTime(0.3, ctx.currentTime);
  oscillator.start();
  oscillator.stop(ctx.currentTime + thoiLuongMs / 1000);
}

export function batDauCanhBaoMuc2() {
  dungCanhBao();  // luôn dừng cảnh báo cũ trước khi bật cái mới, tránh chồng nhiều interval
  intervalId = setInterval(() => phatMotBeep(880, 150), 1000);  // 1 beep/giây
}

export function batDauCanhBaoMuc3() {
  dungCanhBao();
  intervalId = setInterval(() => {
    // cụm 3 beep liên tiếp, cách nhau 200ms
    phatMotBeep(1200, 120);
    setTimeout(() => phatMotBeep(1200, 120), 200);
    setTimeout(() => phatMotBeep(1200, 120), 400);
  }, 2000);  // lặp lại cụm 3 beep mỗi 2 giây
}

export function dungCanhBao() {
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
}
```

**Lưu ý trình duyệt quan trọng**: hầu hết trình duyệt hiện đại **chặn phát âm thanh tự động** nếu chưa có tương tác của người dùng (click) trên trang — gọi là "autoplay policy". Vì vậy `AudioContext` nên được tạo/resume **bên trong 1 event handler** (như `onClick` của nút bất kỳ, ví dụ nút "Bắt đầu theo dõi"), không phải ngay khi component mount.

```jsx
// Cách xử lý phổ biến: tạo AudioContext ngay khi user tương tác lần đầu (ví dụ click bất kỳ đâu trên Dashboard)
useEffect(() => {
  const khoiTaoAmThanh = () => {
    getAudioContext();  // "đánh thức" AudioContext
    document.removeEventListener("click", khoiTaoAmThanh);
  };
  document.addEventListener("click", khoiTaoAmThanh);
  return () => document.removeEventListener("click", khoiTaoAmThanh);
}, []);
```

### 10.4. Kết nối với `alarmLevels.js` và logic mute/snooze

```js
// constants/alarmLevels.js — "nguồn duy nhất" định nghĩa mức độ, theo đúng plan.md mục 4.3
export const ALARM_LEVELS = {
  "BÌNH THƯỜNG": { level: 1, color: "green", sound: false },
  "CẢNH BÁO: TRÊN THẤT (S)": { level: 2, color: "yellow", sound: false },
  "CẢNH BÁO: CHƯA RÕ (Q)": { level: 2, color: "yellow", sound: false },
  "CẢNH BÁO: NHỊP THẤT (V)": { level: 3, color: "red", sound: true },
  "CẢNH BÁO: HỢP NHẤT (F)": { level: 3, color: "red", sound: true },
};
```

Logic mute 2 phút (dùng `useRef` để lưu thời điểm mute, không cần re-render mỗi giây):
```jsx
function useAlarmMute() {
  const [dangMute, setDangMute] = useState(false);
  const [giayConLai, setGiayConLai] = useState(0);

  const mute = () => {
    setDangMute(true);
    setGiayConLai(120);  // 2 phút = 120 giây

    const dem = setInterval(() => {
      setGiayConLai((cu) => {
        if (cu <= 1) {
          clearInterval(dem);
          setDangMute(false);
          return 0;
        }
        return cu - 1;
      });
    }, 1000);
  };

  return { dangMute, giayConLai, mute };
}
```

---

## PHẦN 11: BROWSER NOTIFICATION API

### 11.1. Xin quyền thông báo (Permission)

Trình duyệt yêu cầu **người dùng chủ động cho phép** trước khi web được gửi thông báo hệ thống — đây là quy tắc bảo mật/UX, không thể tự động bật. `plan.md` mục 4.6 yêu cầu nút xin quyền này nằm ở `SettingsPage.jsx`.

```js
async function xinQuyenThongBao() {
  if (!("Notification" in window)) {
    alert("Trình duyệt này không hỗ trợ Notification API");
    return "unsupported";
  }

  if (Notification.permission === "granted") return "granted";

  const ketQua = await Notification.requestPermission();  // hiện popup xin quyền cho user
  // ketQua là 1 trong: "granted" (đồng ý), "denied" (từ chối), "default" (chưa quyết định)
  return ketQua;
}
```

```jsx
function SettingsPage() {
  const [trangThaiQuyen, setTrangThaiQuyen] = useState(Notification.permission);

  const handleXinQuyen = async () => {
    const ketQua = await xinQuyenThongBao();
    setTrangThaiQuyen(ketQua);
  };

  return (
    <div>
      <p>Trạng thái thông báo: {trangThaiQuyen}</p>
      <button onClick={handleXinQuyen} disabled={trangThaiQuyen === "granted"}>
        Bật thông báo trình duyệt
      </button>
    </div>
  );
}
```

### 11.2. Gửi thông báo — chỉ cho mức 3 (Khẩn cấp), đúng yêu cầu `plan.md` mục 4.3

```js
function guiThongBaoKhanCap(tenBenhNhan, nhanChanDoan) {
  if (Notification.permission !== "granted") return;  // im lặng bỏ qua nếu chưa được cấp quyền

  const notification = new Notification("🔴 CẢNH BÁO NHỊP TIM KHẨN CẤP", {
    body: `Bệnh nhân ${tenBenhNhan}: ${nhanChanDoan}`,
    icon: "/heart-icon.png",   // tuỳ chọn, có thể bỏ nếu chưa có icon
    tag: "ecg-alarm",          // dùng chung "tag" để thông báo mới THAY THẾ thông báo cũ, tránh spam
  });

  notification.onclick = () => {
    window.focus();   // đưa tab trình duyệt lên foreground khi bác sĩ bấm vào thông báo
    notification.close();
  };
}
```

Kết nối vào luồng WebSocket (CP4.2, chỉ bắn khi `ALARM_LEVELS[prediction].level === 3`):
```jsx
useEffect(() => {
  if (latestStats.prediction && ALARM_LEVELS[latestStats.prediction]?.level === 3) {
    guiThongBaoKhanCap(activePatient?.name ?? "Không xác định", latestStats.prediction);
    batDauCanhBaoMuc3();
  } else if (ALARM_LEVELS[latestStats.prediction]?.level === 2) {
    batDauCanhBaoMuc2();
  } else {
    dungCanhBao();
  }
}, [latestStats.prediction]);
```

---

## PHẦN 12: XUẤT PDF/CSV (CP4.3)

### 12.1. `html2canvas` — chụp 1 vùng DOM thành ảnh

**Là gì**: thư viện chuyển 1 phần tử HTML (kể cả biểu đồ Plotly render bằng SVG/Canvas bên trong) thành 1 `<canvas>` ảnh, sau đó bạn có thể lấy ảnh đó (`toDataURL`) để nhúng vào PDF.

```bash
npm install html2canvas jspdf
```

```js
import html2canvas from "html2canvas";

async function chupBieuDo(elementRef) {
  const canvas = await html2canvas(elementRef.current, {
    backgroundColor: "#ffffff",  // đảm bảo nền trắng khi in (mặc định có thể trong suốt)
    scale: 2,                     // tăng độ phân giải ảnh chụp (2x), giúp PDF không bị mờ
  });
  return canvas.toDataURL("image/png");  // chuỗi base64 ảnh PNG, dùng thẳng được cho jsPDF
}
```

### 12.2. `jsPDF` — tạo file PDF từ JavaScript

```js
import jsPDF from "jspdf";

function taoBaoCaoPDF({ tenBenhNhan, giuong, chanDoan, anhBieuDo, anhHeatmap, thongKe }) {
  const doc = new jsPDF({ unit: "mm", format: "a4" });  // đơn vị milimet, khổ A4

  // --- Header ---
  doc.setFontSize(16);
  doc.text("BÁO CÁO THEO DÕI ĐIỆN TÂM ĐỒ", 105, 15, { align: "center" });

  doc.setFontSize(11);
  doc.text(`Bệnh nhân: ${tenBenhNhan}`, 15, 30);
  doc.text(`Giường: ${giuong}`, 15, 37);
  doc.text(`Ngày xuất báo cáo: ${new Date().toLocaleString("vi-VN")}`, 15, 44);

  // --- Snapshot biểu đồ ECG ---
  if (anhBieuDo) {
    doc.text("Biểu đồ ECG hiện tại:", 15, 55);
    doc.addImage(anhBieuDo, "PNG", 15, 60, 180, 80);  // x, y, width, height (đơn vị mm)
  }

  // --- Snapshot heatmap Grad-CAM ---
  if (anhHeatmap) {
    doc.addPage();  // sang trang mới cho phần XAI
    doc.text("Phân tích XAI (Grad-CAM) của nhịp đang chọn:", 15, 15);
    doc.addImage(anhHeatmap, "PNG", 15, 20, 180, 80);
  }

  // --- Bảng thống kê ---
  let y = 110;
  doc.text("Thống kê số lần xuất hiện mỗi loại nhịp:", 15, y);
  y += 8;
  Object.entries(thongKe).forEach(([nhan, soLuong]) => {
    doc.text(`${nhan}: ${soLuong} lần`, 20, y);
    y += 7;
  });

  doc.save(`bao-cao-${tenBenhNhan}-${Date.now()}.pdf`);  // trigger download ngay trên trình duyệt
}
```

Kết hợp cả 2 (`ReportButton.jsx`, theo đúng file được chỉ định trong `plan.md` mục 4.4):
```jsx
function ReportButton({ patient, anomalyHistory }) {
  const chartRef = useRef(null);  // gắn vào div bọc ECGChart, xem Phần 3.3

  const handleXuatPDF = async () => {
    const anhBieuDo = await chupBieuDo(chartRef);
    const thongKe = anomalyHistory.reduce((acc, nhip) => {
      acc[nhip.prediction] = (acc[nhip.prediction] || 0) + 1;
      return acc;
    }, {});  // .reduce() — gộp mảng thành 1 object đếm số lần xuất hiện mỗi nhãn

    taoBaoCaoPDF({
      tenBenhNhan: patient.name,
      giuong: patient.bedNumber,
      anhBieuDo,
      thongKe,
    });
  };

  return <button onClick={handleXuatPDF}>Xuất báo cáo PDF</button>;
}
```

**Giải thích `.reduce()`** (hàm mảng thứ 4 bạn cần biết, ngoài `.map/.filter/.find` ở Phần 1.7): nó "gộp" (reduce) toàn bộ mảng thành **1 giá trị duy nhất** — ở đây là 1 object đếm số lần mỗi nhãn xuất hiện. `acc` (accumulator) là kết quả tích luỹ qua từng vòng lặp, bắt đầu từ `{}` (tham số thứ 2 của `.reduce`).

### 12.3. Xuất CSV — dùng `Blob` (không cần thư viện)

**Là gì**: `Blob` (Binary Large Object) là cách trình duyệt biểu diễn dữ liệu thô như 1 file — bạn tạo 1 Blob chứa nội dung CSV dạng text, rồi tạo 1 URL tạm trỏ tới Blob đó để trigger download.

```js
function xuatCSV(anomalyHistory) {
  // Dòng tiêu đề
  const header = "Thời gian,Nhãn AAMI,BPM,Độ tin cậy\n";

  // Mỗi nhịp bất thường thành 1 dòng CSV
  const rows = anomalyHistory
    .map((nhip) => `${nhip.timestamp},${nhip.prediction},${nhip.bpm},${nhip.confidence}`)
    .join("\n");

  const noiDungCSV = header + rows;

  const blob = new Blob([noiDungCSV], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);  // tạo 1 URL tạm thời trỏ tới Blob trong bộ nhớ trình duyệt

  const link = document.createElement("a");  // tạo thẻ <a> "ảo", không hiện lên UI
  link.href = url;
  link.download = `lich-su-canh-bao-${Date.now()}.csv`;
  link.click();  // trigger download như khi user bấm vào link tải file

  URL.revokeObjectURL(url);  // giải phóng bộ nhớ sau khi đã tải xong (dọn dẹp, tránh rò rỉ bộ nhớ)
}
```

**Lưu ý encoding tiếng Việt trong CSV**: nếu mở file CSV này bằng Excel và thấy chữ tiếng Việt bị lỗi font (dấu hỏi/ô vuông), thêm BOM (Byte Order Mark) vào đầu file để Excel nhận đúng UTF-8:
```js
const BOM = "\uFEFF";  // ký tự đặc biệt báo cho Excel biết file này là UTF-8
const blob = new Blob([BOM + noiDungCSV], { type: "text/csv;charset=utf-8;" });
```

---

## PHẦN 13: JWT AUTHENTICATION FLOW & AUTH GUARD (CP5.5)

### 13.1. JWT (JSON Web Token) là gì — hiểu ở mức đủ dùng

JWT là 1 chuỗi mã hoá (không phải mã hoá bí mật hoàn toàn — chỉ **ký số**, ai cũng đọc được nội dung nếu decode, nhưng không thể **giả mạo** vì không có khoá bí mật `JWT_SECRET_KEY` của server) chứa thông tin về người dùng (`sub`, `username`, `role`...) cùng thời hạn hết hạn. Server dùng nó để "nhớ" ai đang đăng nhập mà **không cần lưu session** ở phía server.

Dự án bạn (theo `plan.md` mục 5.3) có **2 loại token**:
- **Access token**: sống 30 phút, dùng để gọi API cần xác thực (đính kèm header `Authorization: Bearer <token>`).
- **Refresh token**: sống 7 ngày, chỉ dùng để xin access token mới khi access token hết hạn — KHÔNG dùng trực tiếp để gọi API nghiệp vụ.

### 13.2. Luồng đăng nhập đầy đủ

```jsx
// context/AuthContext.jsx — bản đầy đủ (mở rộng từ Phần 4.4)
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [dangTaiXacThuc, setDangTaiXacThuc] = useState(true);  // true lúc mới load trang, đang kiểm tra token cũ

  // Lúc app khởi động, kiểm tra xem đã có token lưu từ trước chưa (user chưa logout, chỉ F5 lại trang)
  useEffect(() => {
    async function kiemTraToken() {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setDangTaiXacThuc(false);
        return;
      }
      try {
        const res = await fetch("http://localhost:8000/api/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          setUser(await res.json());
        } else {
          // access token hết hạn -> thử refresh (xem 13.3)
          const thanhCong = await lamMoiToken();
          if (!thanhCong) dangXuat();
        }
      } finally {
        setDangTaiXacThuc(false);
      }
    }
    kiemTraToken();
  }, []);

  const dangNhap = async (username, password) => {
    const res = await fetch("http://localhost:8000/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Đăng nhập thất bại");
    }
    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    setUser({ username, role: data.role });
  };

  const lamMoiToken = async () => {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) return false;
    const res = await fetch("http://localhost:8000/api/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    return true;
  };

  const dangXuat = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, dangTaiXacThuc, dangNhap, dangXuat, lamMoiToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
```

### 13.3. Tự động refresh khi gọi API gặp lỗi 401 — pattern "wrapper cho fetch"

`pccv.md` mục B2 lưu ý: *"access token hết hạn... Frontend nên tự gọi `/api/auth/refresh`... rồi thử lại, chỉ đá về LoginPage nếu refresh cũng thất bại"*. Đóng gói logic này vào 1 hàm dùng chung, tránh lặp code ở mọi nơi gọi API:

```js
// api/authFetch.js
async function authFetch(url, options = {}) {
  const token = localStorage.getItem("access_token");
  let res = await fetch(url, {
    ...options,
    headers: { ...options.headers, Authorization: `Bearer ${token}` },
  });

  if (res.status === 401) {
    const thanhCong = await lamMoiToken();  // gọi hàm ở Phần 13.2
    if (thanhCong) {
      const tokenMoi = localStorage.getItem("access_token");
      // thử lại request BAN ĐẦU với token mới
      res = await fetch(url, {
        ...options,
        headers: { ...options.headers, Authorization: `Bearer ${tokenMoi}` },
      });
    } else {
      window.location.href = "/login";  // refresh cũng thất bại -> đá về trang login
    }
  }

  return res;
}
```

### 13.4. `AuthGuard` — bọc quanh App để chặn truy cập khi chưa đăng nhập

```jsx
// components/AuthGuard.jsx
function AuthGuard({ children }) {
  const { user, dangTaiXacThuc } = useAuth();

  if (dangTaiXacThuc) {
    return <LoadingSpinner />;  // tránh "nháy" LoginPage 1 giây rồi mới vào được app khi F5
  }

  if (!user) {
    return <LoginPage />;  // chưa có token hợp lệ -> CHỈ render LoginPage, không render gì khác
  }

  return children;  // đã đăng nhập -> render App thật
}
```

```jsx
// App.jsx
function App() {
  return (
    <AuthProvider>
      <AuthGuard>
        <Header />
        <Sidebar />
        {/* nội dung app thật */}
      </AuthGuard>
    </AuthProvider>
  );
}
```

### 13.5. Ẩn/hiện theo role (RBAC ở tầng UI)

```jsx
function Sidebar() {
  const { user } = useAuth();

  return (
    <nav>
      <TabLink to="dashboard">Theo Dõi Trực Tuyến</TabLink>
      <TabLink to="patient">Hồ Sơ Bệnh Nhân</TabLink>
      <TabLink to="xai">Phân Tích XAI</TabLink>
      {user?.role === "admin" && <TabLink to="settings">Cài Đặt Hệ Thống</TabLink>}
    </nav>
  );
}
```

```jsx
// Ở XAIPage.jsx — nút "Sửa nhãn" chỉ doctor mới thấy (đúng ví dụ trong plan.md mục 5.6)
{(user?.role === "doctor" || user?.role === "admin") && (
  <button onClick={handleSuaNhan}>Sửa nhãn</button>
)}
```

**Lưu ý bảo mật quan trọng cần hiểu đúng**: việc ẩn nút trên UI **KHÔNG phải là bảo mật thật** — đó chỉ là UX (tránh gây rối cho người dùng không có quyền). Bảo mật thật nằm ở **backend** (`require_role()` dependency, đã làm ở CP5.2/5.4) — dù bạn có ẩn nút hay không, nếu 1 user gửi thẳng request tới API mà không đủ quyền, backend vẫn phải trả về 403. Đây là nguyên tắc "không bao giờ tin tưởng frontend" trong thiết kế bảo mật.

### 13.6. Cách làm KHÔNG bị block bởi Track B (mock server) — đúng gợi ý trong `pccv.md` mục A7

Vì contract API đã cố định sẵn (`plan.md` mục 5.3), bạn có thể build UI + `AuthContext` **trước khi** Track B xong CP5.2, bằng cách tạm thời trả JSON giả đúng contract:

```js
// mock/authMock.js — DÙNG TẠM, xoá khi Track B báo CP5.2 xong
export async function mockLogin(username, password) {
  await new Promise((r) => setTimeout(r, 300));  // giả lập độ trễ mạng
  if (username === "admin" && password === "Admin@123") {
    return {
      access_token: "fake.access.token",
      refresh_token: "fake.refresh.token",
      token_type: "bearer",
      role: "admin",
    };
  }
  throw { response: { status: 401, data: { detail: "Sai tài khoản hoặc mật khẩu" } } };
}
```

Cách "cắm API thật vào sau" gọn nhất: định nghĩa 1 biến `USE_MOCK` (hoặc biến môi trường Vite `import.meta.env.VITE_USE_MOCK`), rồi rẽ nhánh gọi `mockLogin` hoặc `fetch` thật — khi Track B báo xong, chỉ cần đổi giá trị biến này, **không sửa logic nào khác** trong `AuthContext`.

---

## PHẦN 14: TESTING VỚI VITEST + REACT TESTING LIBRARY (CP6.2 — phần Frontend)

### 14.1. Cài đặt

Theo đúng `plan.md` mục 6.2: *"thêm `vitest` + `@testing-library/react` vào `package.json`"*.

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

Thêm vào `vite.config.js`:
```js
export default {
  // ...cấu hình có sẵn
  test: {
    environment: "jsdom",       // giả lập DOM trình duyệt trong Node.js để test chạy được
    globals: true,               // dùng test/expect mà không cần import mỗi file
    setupFiles: "./src/test-setup.js",
  },
};
```

```js
// src/test-setup.js
import "@testing-library/jest-dom";  // thêm các matcher hữu ích như .toBeInTheDocument()
```

Thêm script vào `package.json`: `"test": "vitest run"`.

### 14.2. Test 1 component thuần UI — `PatientForm` (đúng yêu cầu `plan.md` mục 6.2)

**Nguyên tắc cốt lõi của React Testing Library**: test **hành vi người dùng thấy được** (bấm nút, gõ chữ, thấy chữ hiện lên), KHÔNG test chi tiết cài đặt bên trong (không kiểm tra `state` nội bộ trực tiếp).

```jsx
// PatientForm.test.jsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import PatientForm from "./PatientForm";

describe("PatientForm", () => {
  it("báo lỗi khi để trống tên bệnh nhân", () => {
    const handleSubmit = vi.fn();  // "spy" — hàm giả để kiểm tra có được gọi hay không
    render(<PatientForm onSubmit={handleSubmit} danhSachHienTai={[]} />);

    const nutLuu = screen.getByText("Lưu");
    fireEvent.click(nutLuu);  // giả lập user bấm nút Lưu mà chưa gõ gì

    expect(screen.getByText("Họ tên là bắt buộc")).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();  // submit KHÔNG được gọi vì có lỗi validate
  });

  it("gọi onSubmit với dữ liệu đúng khi form hợp lệ", () => {
    const handleSubmit = vi.fn();
    render(<PatientForm onSubmit={handleSubmit} danhSachHienTai={[]} />);

    fireEvent.change(screen.getByPlaceholderText("Họ tên"), {
      target: { value: "Nguyễn Văn A" },
    });
    fireEvent.change(screen.getByPlaceholderText("Tuổi"), {
      target: { value: "60" },
    });
    fireEvent.click(screen.getByText("Lưu"));

    expect(handleSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ name: "Nguyễn Văn A", age: "60" })
    );
  });

  it("từ chối tuổi ngoài khoảng 0-120", () => {
    const handleSubmit = vi.fn();
    render(<PatientForm onSubmit={handleSubmit} danhSachHienTai={[]} />);

    fireEvent.change(screen.getByPlaceholderText("Họ tên"), { target: { value: "A" } });
    fireEvent.change(screen.getByPlaceholderText("Tuổi"), { target: { value: "200" } });
    fireEvent.click(screen.getByText("Lưu"));

    expect(screen.getByText("Tuổi phải trong khoảng 0-120")).toBeInTheDocument();
  });
});
```

### 14.3. Test hàm JS thuần (không phải component) — `alarmAudio`, `reportGenerator`

Với logic thuần JS (không phải component React), test đơn giản hơn nhiều — không cần `render`, chỉ gọi hàm và kiểm tra kết quả.

```js
// alarmLevels.test.js
import { describe, it, expect } from "vitest";
import { ALARM_LEVELS } from "./alarmLevels";

describe("alarmLevels", () => {
  it("nhãn BÌNH THƯỜNG có mức độ 1, không âm thanh", () => {
    expect(ALARM_LEVELS["BÌNH THƯỜNG"].level).toBe(1);
    expect(ALARM_LEVELS["BÌNH THƯỜNG"].sound).toBe(false);
  });

  it("nhãn NHỊP THẤT (V) có mức độ 3, có âm thanh", () => {
    expect(ALARM_LEVELS["CẢNH BÁO: NHỊP THẤT (V)"].level).toBe(3);
    expect(ALARM_LEVELS["CẢNH BÁO: NHỊP THẤT (V)"].sound).toBe(true);
  });
});
```

```js
// reportGenerator.test.js — test hàm serialize CSV (mục "CSV serializer" trong plan.md mục 6.2)
import { describe, it, expect } from "vitest";
import { taoNoiDungCSV } from "./reportGenerator";  // giả sử tách riêng hàm tạo string CSV để dễ test (không đụng DOM)

describe("taoNoiDungCSV", () => {
  it("tạo đúng số dòng và đúng header", () => {
    const lichSu = [
      { timestamp: "2026-08-30T10:00:00Z", prediction: "CẢNH BÁO: NHỊP THẤT (V)", bpm: 110, confidence: 0.95 },
    ];
    const csv = taoNoiDungCSV(lichSu);
    const dongs = csv.trim().split("\n");

    expect(dongs.length).toBe(2);  // 1 dòng header + 1 dòng dữ liệu
    expect(dongs[0]).toBe("Thời gian,Nhãn AAMI,BPM,Độ tin cậy");
    expect(dongs[1]).toContain("CẢNH BÁO: NHỊP THẤT (V)");
  });

  it("trả về chỉ header khi lịch sử rỗng", () => {
    const csv = taoNoiDungCSV([]);
    expect(csv.trim().split("\n").length).toBe(1);
  });
});
```

**Bài học thiết kế quan trọng rút ra từ ví dụ trên**: để test dễ dàng, hãy **tách logic thuần (tạo chuỗi CSV) ra khỏi phần thao tác DOM** (`Blob`/`URL.createObjectURL`/`link.click()`). Hàm `taoNoiDungCSV(data)` chỉ nhận dữ liệu, trả về chuỗi — test được trực tiếp không cần giả lập trình duyệt. Hàm `xuatCSV(data)` gọi `taoNoiDungCSV` rồi mới làm phần DOM — phần DOM này khó test hơn nên thường được bỏ qua hoặc test tối giản.

### 14.4. Chạy test

```bash
npm run test
```

DoD theo `plan.md` mục 6.2: *"`npm run test` (Vitest) xanh hết"*.

---

## PHẦN 15: GIT WORKFLOW CHO DỰ ÁN 2 NGƯỜI (theo đúng `pccv.md` mục 0)

Đây không phải kiến thức "Frontend" thuần tuý, nhưng là quy trình bắt buộc để làm việc đúng với Track B mà không xung đột code.

### 15.1. Quy trình 1 sub-checkpoint — 5 bước

```bash
# Bước 1: LUÔN bắt đầu từ main mới nhất
git checkout main
git pull

# Bước 2: tạo nhánh riêng cho sub-checkpoint, đặt tên đúng format feat/<cp-id>-<mo-ta-ngan>
git checkout -b feat/cp3.6-connect-frontend-api

# Bước 3: code, commit thường xuyên với message rõ ràng
git add frontend/src/components/dashboard/RecordSelector.jsx
git commit -m "CP3.6: thêm RecordSelector gọi GET /api/records"

# ... tiếp tục code + commit cho tới khi xong cả sub-checkpoint

# Bước 4: đẩy nhánh lên, mở Pull Request vào main
git push -u origin feat/cp3.6-connect-frontend-api
# rồi lên GitHub tạo PR, nhờ Track B review nhanh

# Bước 5: sau khi merge — quay lại bước 1, bắt đầu sub-checkpoint tiếp theo
```

### 15.2. Quy tắc "vùng" tránh xung đột (theo `pccv.md` mục 0.2)

Track A **chỉ được sửa**: `frontend/**`. Chỉ **đọc** (không sửa) `plan.md`/`pccv.md`/`README.md`, **trừ** việc tick `[x]` đúng dòng sub-checkpoint của mình trong `plan.md` khi xong (mục 0.3b của `pccv.md`) — vì mỗi người chỉ tick dòng riêng nên hiếm khi đụng nhau.

Nếu cần sửa file **ngoài** `frontend/**` (ví dụ phát hiện cần đổi thứ gì đó ở backend) mà **không** nằm trong danh sách "Yêu cầu chéo track" đã ghi sẵn trong `plan.md` → nhắn hỏi Track B trước, đừng tự sửa.

### 15.3. Sau mỗi sub-checkpoint xong — báo đúng 3 bước (theo `pccv.md` mục 0.3)

1. Chạy đúng lệnh test/DoD ghi trong `plan.md` cho sub-checkpoint đó (ví dụ CP3.6: test đổi record 100/208 thủ công; CP4.1: kiểm tra CRUD + dữ liệu còn sau F5).
2. Tick `[x]` vào đúng dòng sub-checkpoint trong `plan.md` phần III.
3. Đăng đúng nội dung báo cáo đã quy định sẵn trong `pccv.md` mục 2 (ví dụ: *"CP3.6 xong — Dashboard giờ có BPM/HRV/chọn bản ghi/upload, PR #___"*) — để Track B biết interface đã sẵn sàng dùng.

---

## PHẦN 16: LỘ TRÌNH HỌC TẬP GỢI Ý — HỌC GÌ TRƯỚC KHI LÀM SUB-CHECKPOINT NÀO

Sắp xếp đúng theo thứ tự công việc thật của bạn (khớp `pccv.md` mục 5 — Sprint 1-4):

| Tuần | Việc làm | Học trước (theo phần trong giáo trình này) |
|:---|:---|:---|
| Tuần 1 (đầu) | **CP3.6** — Nối Frontend với API CP3 | Phần 1 (JS hiện đại) → Phần 2 (Component/Props) → Phần 3 (Hooks, đặc biệt `useEffect`) → Phần 5 (Fetch) → Phần 6 (WebSocket) |
| Tuần 1 (cuối) → Tuần 2 (đầu) | **CP4.1** — Patient Management UI | Phần 4 (Context) → Phần 8 (localStorage) → Phần 9 (Form & Validation) |
| Tuần 2 | **CP4.2** — Alarm System | Phần 10 (Web Audio) → Phần 11 (Notification) |
| Tuần 2 (cuối) → Tuần 3 | **CP4.3** — Report Exporter | Phần 12 (PDF/CSV) — cần nắm chắc `useRef` (Phần 3.3) trước |
| Tuần 3 | **CP4.4** — XAI Explainer rút gọn | Phần 7 (Plotly — chỉ cần đọc hiểu, không cần build lại từ đầu) |
| Tuần 3 (cuối) | **CP4.5** — Settings Page | Ôn lại Phần 4 + Phần 8 |
| Tuần 4 | **CP5.5** — Auth Guard | Phần 13 (JWT, đọc kỹ mục 13.6 về cách làm song song không bị block) |
| Bất kỳ lúc nào rảnh, viết test cho phần vừa xong | **CP6.2 (Frontend)** | Phần 14 (Vitest) |
| Xuyên suốt | Quy trình làm việc | Phần 15 (Git workflow) |

**Lời khuyên học tập cuối cùng**: đừng cố học hết cả 16 phần rồi mới bắt đầu code. Cách hiệu quả nhất là **học đúng phần cần cho sub-checkpoint đang làm, code luôn, gặp lỗi thì quay lại đọc kỹ hơn phần liên quan**. React là kỹ năng hình thành qua thực hành lặp đi lặp lại (đặc biệt là trực giác về `useEffect` dependency array) — bạn sẽ thấy nó "vỡ ra" rõ ràng nhất sau khi tự debug 1-2 lỗi thực tế do quên cleanup WebSocket hoặc quên spread state, chứ không phải chỉ đọc lý thuyết.

Chúc bạn làm Track A suôn sẻ!
