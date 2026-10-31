# -*- coding: utf-8 -*-
"""
Generate the complete 18-slide Master Presentation Script for NEURO-ECG
Samsung Innovation Campus (SIC) 2026 — Hanoi University of Science and Technology (HUST)
Presenters:
- Nguyen Dao Nam Hai (Team Leader): Slides 1 - 10
- Phan Thi Hai Yen (Member): Slides 11 - 18
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_callout(doc, title, text, bg_hex="F0F4F8", border_hex="0A2540"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=130, bottom=130, left=180, right=180)
    
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="36" w:space="0" w:color="{border_hex}"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    cell._tc.get_or_add_tcPr().append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    run_t = p.add_run(f"★ {title}\n")
    run_t.font.name = 'Calibri'
    run_t.font.size = Pt(11)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(10, 37, 64)
    
    run_c = p.add_run(text)
    run_c.font.name = 'Calibri'
    run_c.font.size = Pt(10)
    run_c.font.color.rgb = RGBColor(40, 45, 55)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_after = Pt(4)

def build_full_script():
    doc = docx.Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
        
    NAVY = RGBColor(10, 37, 64)       # #0A2540
    BLUE = RGBColor(0, 114, 206)      # #0072CE
    DARK = RGBColor(33, 37, 41)       # #212529
    MUTED = RGBColor(100, 110, 120)
    GREEN = RGBColor(16, 124, 65)
    AMBER = RGBColor(217, 119, 6)
    
    # HEADER
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(0)
    p_pre.paragraph_format.space_after = Pt(2)
    run_pre = p_pre.add_run("SAMSUNG INNOVATION CAMPUS (SIC) 2026 — ĐẠI HỌC BÁCH KHOA HÀ NỘI")
    run_pre.font.name = 'Calibri'
    run_pre.font.size = Pt(10.5)
    run_pre.font.bold = True
    run_pre.font.color.rgb = BLUE
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(4)
    run_title = p_title.add_run("KỊCH BẢN THUYẾT TRÌNH BẢO VỆ CAPSTONE PROJECT SIÊU CHI TIẾT\nTOÀN BỘ 18 SLIDE (CHUẨN 5 UNIT SAMSUNG SIC)")
    run_title.font.name = 'Calibri'
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(12)
    run_sub = p_sub.add_run("Dự án: NEURO-ECG — Hệ thống Giám sát ECG Thời gian thực Tích hợp AI Giải thích được & Hỗ trợ Chẩn đoán Rối loạn Nhịp tim Đa tầng")
    run_sub.font.name = 'Calibri'
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = MUTED
    
    # META INFO BOX
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Nhóm tác giả:", "Nguyễn Đào Nam Hải (Team Leader) & Phan Thị Hải Yến (Co-presenter)"),
        ("Phân chia vai trò:", "Nam Hải (Slide 01 – 10: Unit 1 & 2) | Hải Yến (Slide 11 – 18: Unit 3, 4, 5)"),
        ("Tổng thời lượng:", "15.0 – 16.0 phút (Khung bảo vệ Capstone chuẩn Samsung Innovation Campus)"),
        ("Liên kết Slide Canva:", "https://www.canva.com/design/DAHY8BfIJ2Y/eoFW8mGXUPELV4omJlY3tQ/edit")
    ]
    for idx, (lbl, val) in enumerate(meta_data):
        row = meta_table.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.6)
        set_cell_background(c0, "F4F6F9")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
        
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(lbl)
        r0.font.bold = True
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = NAVY
        
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(val)
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = DARK
    
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(10)
    p_div.paragraph_format.space_after = Pt(4)
    
    # STRATEGY BOX
    add_callout(
        doc,
        "CHIẾN LƯỢC SÂN KHẤU VÀ TÂM THẾ THUYẾT TRÌNH BẢO VỆ CAPSTONE SIC",
        "1. KHẮC PHỤC TRIỆT ĐỂ LỖI 'NGANG ĐỌC': Slide là bức tranh trực quan cho Hội đồng nhìn số liệu và đồ thị; lời nói của hai bạn là câu chuyện kỹ thuật logic, đĩnh đạc và thuyết phục. Tuyệt đối không đọc lại từng dòng gạch đầu dòng.\n"
        "2. TỰ TIN ĐỊNH VỊ HỆ THỐNG Y TẾ: Xóa bỏ mọi sự rào đón tự ti. NEURO-ECG được định vị chính xác là 'Hệ thống Hỗ trợ Ra quyết định Lâm sàng' (Clinical Decision Support System - CDSS) tuyến đầu 24/7 giúp giải phóng 80% áp lực đọc bản ghi Holter cho bác sĩ tim mạch.\n"
        "3. LÀM CHỦ SỐ LIỆU ĐỊNH LƯỢNG: Nắm chắc các con số vàng: Test Accuracy 98.57%, F1-macro 92.39%, F1 Pan-Tompkins 97.14%, ONNX INT8 nén 74.5% còn 697.3 KB (< 700 KB nhúng), Độ lệch Val-Test chỉ 0.11% (không leak), 42/42 tests pass.\n"
        "4. ĂN Ý TUYỆT ĐỐI GIỮA HAI BẠN: Nam Hải làm chủ chiều sâu AI Core, XAI, DSP và Tối ưu nhúng; Hải Yến làm chủ luồng thực nghiệm, kiểm thử QA, Live Demo trực quan và phân tích Domain Shift.",
        bg_hex="EBF3FA",
        border_hex="0072CE"
    )

    # 18 SLIDES DATA
    slides = [
        # SLIDE 1
        {
            "num": 1,
            "speaker": "Nguyễn Đào Nam Hải (Team Leader)",
            "title": "Tiêu Đề Dự Án & Định Danh Nhóm",
            "unit": "Unit 00 — Title Slide",
            "time": "40 giây (Tích lũy: 0:40)",
            "goal": "Tạo ấn tượng trang trọng, khoa học công nghệ, chuẩn nhận diện Samsung Innovation Campus & Đại học Bách khoa Hà Nội.",
            "cues": "Đứng trung tâm sân khấu, mắt nhìn thẳng vào Hội đồng, mỉm cười nhẹ và cúi chào đầu trang trọng. Giọng nói trầm ấm, vang rõ.",
            "speech": (
                "Kính thưa quý thầy cô trong Hội đồng Giám khảo Samsung Innovation Campus, quý thầy cô Đại học Bách khoa Hà Nội "
                "và toàn thể các bạn có mặt trong buổi bảo vệ Capstone Project ngày hôm nay.\n\n"
                "Em là Nguyễn Đào Nam Hải, đại diện cho nhóm tác giả gồm em và bạn Phan Thị Hải Yến, xin được trân trọng báo cáo "
                "kết quả đề tài tốt nghiệp: 'NEURO-ECG: Hệ thống giám sát tín hiệu điện tim thời gian thực, tích hợp Trí tuệ nhân tạo "
                "giải thích được (Explainable AI) và hỗ trợ chẩn đoán rối loạn nhịp tim đa tầng'.\n\n"
                "Dự án của chúng em được phát triển với định hướng kết nối toàn diện từ tầng xử lý tín hiệu số y sinh (DSP), "
                "mô hình học sâu tối ưu hóa lượng tử nhúng, cho tới ứng dụng Web lâm sàng thời gian thực hỗ trợ bác sĩ ra quyết định. "
                "Hôm nay, em xin phép đại diện nhóm dẫn dắt toàn bộ nội dung nghiên cứu cốt lõi và kiến trúc kỹ thuật của hệ thống."
            ),
            "defense": (
                "Q: Dự án này là bài tập môn học hay là một sản phẩm kỹ thuật hoàn chỉnh?\n"
                "A: Dạ thưa Hội đồng, NEURO-ECG là sản phẩm kỹ thuật y tế hoàn chỉnh cấp độ Capstone (TRL-4/5), được triển khai "
                "đủ 5 tầng: từ luồng Ingestion 360Hz, thuật toán DSP Pan-Tompkins, mô hình ResNet-1D đạt 98.57% test accuracy, "
                "lượng tử hóa ONNX INT8 dưới 700 KB, cho tới Full-stack Web có phân quyền bác sĩ, báo động chuẩn y tế IEC 60601-1-8 "
                "và 42/42 bài kiểm thử tự động CI/CD."
            ),
            "transition": "Để quý Hội đồng tiện theo dõi lộ trình báo cáo, em xin phép đi vào cấu trúc 5 phần của buổi bảo vệ ngày hôm nay."
        },
        # SLIDE 2
        {
            "num": 2,
            "speaker": "Nguyễn Đào Nam Hải (Team Leader)",
            "title": "Table of Contents — Khung Báo Cáo 5 Unit Chuẩn Samsung SIC",
            "unit": "Unit 00 — Agenda",
            "time": "30 giây (Tích lũy: 1:10)",
            "goal": "Khái quát cấu trúc báo cáo logic theo quy chuẩn 5 Unit của Samsung SIC, phân định rõ phạm vi 10 slide đầu của Nam Hải và 8 slide sau của Hải Yến.",
            "cues": "Bàn tay mở hướng về màn chiếu (không chỉ trỏ 1 ngón). Nói dứt khoát, nhịp điệu nhanh gọn.",
            "speech": (
                "Báo cáo của chúng em tuân thủ nghiêm ngặt khung đánh giá 5 Unit chuẩn của Samsung Innovation Campus:\n"
                "• Unit 1: Tổng quan bối cảnh lâm sàng, động lực nghiên cứu, mục tiêu định lượng và phân công công việc.\n"
                "• Unit 2: Quá trình thực hiện kỹ thuật — tập trung vào luồng DSP, đối sánh 5 kiến trúc AI, giải thích mô hình với 1D Grad-CAM và tối ưu nhúng ONNX INT8.\n"
                "• Unit 3: Kết quả thực nghiệm và phiên Live Demonstration hệ thống trực tiếp.\n"
                "• Unit 4: Đánh giá tác động thực tiễn, phân tích Domain Shift đa nguồn và các rào cản kỹ thuật.\n"
                "• Unit 5: Tự đánh giá năng lực nhóm, bài học kinh nghiệm và lộ trình thương mại hóa.\n\n"
                "Trong phần đầu tiên, em sẽ trình bày chi tiết Unit 1 và Unit 2. Sau đó, bạn Hải Yến sẽ trực tiếp điều hành phiên Live Demo và kết quả tại Unit 3, 4, 5."
            ),
            "defense": (
                "Q: Vì sao nhóm lại phân chia bài thuyết trình theo hai nửa như vậy?\n"
                "A: Dạ thưa thầy cô, em trực tiếp thiết kế kiến trúc hệ thống, huấn luyện lõi AI, XAI và đóng gói nhúng; "
                "còn bạn Hải Yến phụ trách luồng dữ liệu, thẩm định DSP, kiểm thử QA và chuẩn hóa giao diện lâm sàng. Cách phân chia "
                "này đảm bảo người phụ trách chuyên sâu mảng nào sẽ trực tiếp báo cáo và chịu trách nhiệm phản biện sâu nhất mảng đó trước Hội đồng."
            ),
            "transition": "Ngay sau đây, em xin kính mời Hội đồng bước vào Unit 1 với bối cảnh lâm sàng và bài toán cốt lõi."
        },
        # SLIDE 3
        {
            "num": 3,
            "speaker": "Nguyễn Đào Nam Hải (Team Leader)",
            "title": "Unit 1.1: Bối Cảnh Lâm Sàng & 2 Rào Cản Cốt Tử của AI Y Tế",
            "unit": "Unit 01 — Introduction",
            "time": "50 giây (Tích lũy: 2:00)",
            "goal": "Chỉ ra nỗi đau lớn nhất của tim mạch (quá tải bản ghi Holter 24h, nguy cơ đột tử) và vạch rõ 2 rào cản chí mạng: Hộp đen (Black-box) và Thiếu chuỗi tích hợp y tế.",
            "cues": "Giọng nói hạ thấp trầm ấm tạo tính nghiêm túc của bài toán cứu người. Nhấn mạnh 2 chữ: 'Hộp đen' và 'Tích hợp chuẩn'.",
            "speech": (
                "Thưa quý Hội đồng, bệnh lý tim mạch hiện là nguyên nhân gây tử vong số một toàn cầu. Trong đó, các rối loạn nhịp tim nguy hiểm "
                "như Ngoại tâm thu thất (PVC) kéo dài hay Rung nhĩ (AFib) thường diễn tiến âm thầm nhưng có thể dẫn đến đột tử hoặc đột quỵ não chỉ sau vài phút.\n\n"
                "Tại các phòng cấp cứu và hồi sức tích cực, một bệnh nhân đeo máy Holter 24 giờ tạo ra hơn 100.000 nhịp tim. Các bác sĩ tim mạch "
                "đang phải đối mặt với tình trạng quá tải nghiêm trọng khi đọc bản ghi thủ công.\n\n"
                "Tuy nhiên, khi đưa Trí tuệ nhân tạo vào hỗ trợ y tế, chúng em nhận thấy có 2 rào cản sống còn:\n"
                "Thứ nhất là 'Nghịch lý Hộp Đen' (Black-Box Problem): Đa số các mô hình AI chỉ trả về một xác suất vô hồn. Bác sĩ không thể tin tưởng "
                "và không thể ký lệnh điều trị nếu không biết AI dựa trên căn cứ hình thái sóng nào.\n"
                "Thứ hai là 'Sự thiếu hụt chuỗi tích hợp y tế': Hầu hết các nghiên cứu dừng lại ở file notebook rời rạc, hoàn toàn "
                "thiếu chuỗi lọc nhiễu thực tế, thiếu streaming thời gian thực và không có quy trình lưu vết trách nhiệm bác sĩ (Audit Trail).\n\n"
                "Đó chính là lý do dự án NEURO-ECG ra đời để giải quyết triệt để cả hai bài toán này."
            ),
            "defense": (
                "Q: Hệ thống này có tham vọng thay thế bác sĩ tim mạch hay không?\n"
                "A: Dạ hoàn toàn không ạ! Chúng em định vị NEURO-ECG là một 'Hệ thống Hỗ trợ Ra quyết định Lâm sàng' (Clinical Decision Support System - CDSS). "
                "AI đóng vai trò như một màng lọc cảnh báo sớm tuyến đầu 24/7, tự động khoanh vùng các biến cố nghi ngờ và giải thích bằng hình ảnh. "
                "Quyết định chẩn đoán và điều trị cuối cùng luôn luôn thuộc về bác sĩ có chứng chỉ hành nghề, được hỗ trợ bởi cơ chế duyệt nhãn Human-in-the-loop của chúng em."
            ),
            "transition": "Xuất phát từ bối cảnh đó, nhóm đã xác lập 5 mục tiêu nghiên cứu và các KPI kỹ thuật định lượng cụ thể tại Slide tiếp theo."
        },
        # SLIDE 4
        {
            "num": 4,
            "speaker": "Nguyễn Đào Nam Hải (Team Leader)",
            "title": "Unit 1.2: 5 Trụ Cột Đột Phá & Mục Tiêu Định Lượng NEURO-ECG",
            "unit": "Unit 01 — Introduction",
            "time": "50 giây (Tích lũy: 2:50)",
            "goal": "Trình bày 5 trụ cột sản phẩm vững chắc và 'bắn' số liệu KPI thực nghiệm đo đạc độc lập (98.57% Acc, 92.39% F1-macro, 97.14% Pan-Tompkins, < 700 KB INT8).",
            "cues": "Chỉ tay dứt khoát vào 5 khối thẻ trên màn chiếu. Tốc độ nói nhanh, tự tin, nhấn mạnh các con số định lượng chính xác.",
            "speech": (
                "Để giải quyết triệt để bài toán đặt ra, NEURO-ECG được xây dựng dựa trên 5 trụ cột kỹ thuật then chốt:\n"
                "1. AI Core Đa Mô Hình: Nghiên cứu, huấn luyện và đối sánh 5 kiến trúc mạng nơ-ron 1D. Trong đó mô hình ResNet-1D của chúng em đạt "
                "độ chính xác 98.57% và F1-Macro 92.39% trên tập test MIT-BIH chuẩn, với độ trễ suy luận siêu thấp chỉ 0.134 miligiây.\n"
                "2. Explainable AI: Tích hợp thuật toán 1D Grad-CAM đầu tiên trên sóng điện tim, bóc tách vùng đóng góp tế vi trên phức bộ P-QRS-T giúp bác sĩ soi chiếu trực quan.\n"
                "3. Kỹ Thuật Y Sinh DSP: Xây dựng bộ lọc thông dải Butterworth 0.5–45Hz, lọc Notch 50Hz triệt tiêu nhiễu điện lưới, cùng thuật toán Pan-Tompkins phát hiện đỉnh R đạt F1 trung bình 97.14% trên 8 bản ghi PhysioNet.\n"
                "4. Tối Ưu Edge AI: Lượng tử hóa ONNX INT8 thành công, nén 74.5% dung lượng xuống 697.3 KB — hoàn thành xuất sắc cam kết trong đề cương dự án là dưới 700 KB để sẵn sàng nạp lên chip đeo tay.\n"
                "5. Và cuối cùng là Nền Tảng Full-Stack: Truyền phát WebSocket 360Hz 2 kênh liên tục, giao diện React 19 đạt 60 khung hình/giây và cơ chế phân quyền bảo mật 3 vai trò cùng Audit Trail chuẩn y tế."
            ),
            "defense": (
                "Q: Con số F1-macro 92.39% và 91.70% ở các bảng có gì mâu thuẫn không?\n"
                "A: Dạ thưa thầy cô, 91.70% là kết quả trong bảng đối sánh benchmark lịch sử của 5 mô hình ban đầu tại Checkpoint 2. "
                "Còn 92.39% là kết quả kiểm định chính thức đo lại trên checkpoint mô hình tốt nhất vào ngày 23/10 có gắn mã băm SHA-256 truy vết trong phụ lục báo cáo. "
                "Cả hai con số đều phản ánh năng lực vượt trội của mô hình trên tập kiểm thử độc lập."
            ),
            "transition": "Để hoàn thành trọn vẹn 5 trụ cột kỹ thuật này, nhóm đã phân công vai trò và tổ chức tiến độ ra sao? Kính mời Hội đồng cùng nhìn vào Slide 05."
        },
        # SLIDE 5
        {
            "num": 5,
            "speaker": "Nguyễn Đào Nam Hải (Team Leader)",
            "title": "Unit 1.3 & 1.4: Phân Công Trách Nhiệm & Tiến Độ 6 Checkpoints",
            "unit": "Unit 01 — Introduction",
            "time": "45 giây (Tích lũy: 3:35)",
            "goal": "Chứng minh năng lực quản trị dự án chuyên nghiệp, hoàn thành 100% đúng hạn qua 6 Checkpoints khắt khe, thể hiện sự ăn ý tuyệt đối giữa hai thành viên.",
            "cues": "Ánh mắt nhìn sang bạn đồng hành Hải Yến như một sự ghi nhận đồng đội, sau đó quay lại Hội đồng với phong thái tự tin.",
            "speech": (
                "Trong dự án này, sự phân công trách nhiệm được xác lập dựa trên thế mạnh chuyên môn sâu của từng thành viên:\n"
                "• Em — Nam Hải đảm nhận vai trò Trưởng nhóm, trực tiếp thiết kế kiến trúc hệ thống, nghiên cứu lõi AI ResNet-1D, giải thuật 1D Grad-CAM, "
                "tối ưu hóa lượng tử hóa ONNX INT8, lập trình Backend FastAPI WebSocket và hạ tầng Docker CI/CD.\n"
                "• Bạn Phan Thị Hải Yến phụ trách mảng Kỹ thuật Dữ liệu & DSP y sinh: thu thập chuẩn hóa tập dữ liệu MIT-BIH, PhysioNet WFDB, "
                "cài đặt thuật toán lọc thích nghi và Pan-Tompkins, đồng thời phụ trách thẩm định độ chính xác và kiểm thử QA toàn diện.\n\n"
                "Về mặt quản trị tiến độ (WBS), nhóm đã hoàn thành xuất sắc 100% toàn bộ 6 Checkpoints theo đúng kế hoạch:\n"
                "Từ Checkpoint 1 & 2 xây dựng mô hình AI và pipeline dữ liệu; Checkpoint 3 & 4 tích hợp DSP đỉnh R và chuẩn hóa cảnh báo y tế IEC 60601-1-8; "
                "cho đến Checkpoint 5 & 6 hoàn thiện hệ thống cơ sở dữ liệu RBAC, Audit Trail và bộ 42 test cases tự động."
            ),
            "defense": (
                "Q: Trong 6 tuần thực hiện, khó khăn lớn nhất trong việc phối hợp nhóm là gì?\n"
                "A: Dạ thưa Hội đồng, thách thức lớn nhất là sự bất đồng bộ giữa miền tần số lấy mẫu của dữ liệu thô (PhysioNet 360Hz) "
                "và định dạng đầu vào của mô hình huấn luyện (125Hz, 187 mẫu). Nhóm đã phải thảo luận kỹ lưỡng và thống nhất một giao thức "
                "resampling Polyphase chặt chẽ trong tầng tiền xử lý để vừa bảo toàn biên độ phức bộ QRS, vừa đảm bảo mô hình nhận diện chính xác."
            ),
            "transition": "Sau đây, em xin phép bước vào Unit 2: Quá trình thực hiện kỹ thuật, mở đầu bằng Kiến trúc tổng thể 5 tầng của hệ thống."
        },
        # SLIDE 6
        {
            "num": 6,
            "speaker": "Nguyễn Đào Nam Hải (Team Leader)",
            "title": "Unit 2.1: Kiến Trúc Hệ Thống 5 Tầng Luồng Dữ Liệu Thời Gian Thực",
            "unit": "Unit 02 — Project Execution",
            "time": "55 giây (Tích lũy: 4:30)",
            "goal": "Làm chủ sơ đồ kiến trúc End-to-End từ Ingestion 360Hz đến UI, giải thích cơ chế Singleton Engine, hàng đợi bất đồng bộ và luồng WebSocket hai chiều.",
            "cues": "Dùng tay hoặc laser pointer quét tuần tự từ Trái qua Phải (Tầng 1 -> Tầng 5), làm nổi bật tính liên tục và khép kín của luồng dữ liệu.",
            "speech": (
                "Thưa quý Hội đồng, đây là Kiến trúc 5 tầng của NEURO-ECG — được thiết kế theo mô hình vi dịch vụ hướng sự kiện (Event-Driven Architecture) "
                "nhằm đảm bảo độ trễ thấp nhất và tính ổn định cao nhất:\n\n"
                "• Tầng 1 — Ingestion Layer: Nhận luồng tín hiệu điện tim 2 kênh thô (Lead MLII và Lead V1) ở tần số 360Hz. Dữ liệu được đóng gói thành "
                "36 gói tin mỗi giây (mỗi gói 10 mẫu) và truyền phát qua giao thức WebSocket bất đồng bộ.\n"
                "• Tầng 2 — Tiền Xử Lý DSP: Ngay khi nhận tín hiệu, bộ lọc Butterworth và Notch 50Hz tiến hành khử nhiễu đường nền và nhiễu điện lưới; "
                "sau đó thuật toán Pan-Tompkins quét tìm đỉnh R theo thời gian thực.\n"
                "• Tầng 3 — AI Inference (Thiết kế theo mẫu Singleton Pattern): Mỗi khi phát hiện một đỉnh R, hệ thống trích xuất cửa sổ 187 mẫu quanh đỉnh, "
                "chuẩn hóa và nạp vào mô hình ResNet-1D / ONNX INT8. Mô hình suy luận trong 0.13 miligiây để trả về phân loại nhịp và bản đồ nhiệt Grad-CAM.\n"
                "• Tầng 4 — Điều Phối Cảnh Báo: Phân tầng nguy cơ thành 3 cấp (Bình thường - Chú ý - Nguy cấp) và kích hoạt chuông báo động tuân thủ tiêu chuẩn an toàn thiết bị y tế IEC 60601-1-8.\n"
                "• Tầng 5 — Giao Diện Lâm Sàng & Duyệt Nhãn: Hiển thị sóng điện tim 60 FPS trên React 19, cho phép bác sĩ thẩm định, sửa nhãn sai và lưu vết vĩnh viễn vào hệ cơ sở dữ liệu."
            ),
            "defense": (
                "Q: Tại sao phải dùng Singleton Pattern cho mô hình AI ở Tầng 3?\n"
                "A: Dạ thưa thầy cô, việc khởi tạo lại mô hình và cấp phát lại bộ nhớ trọng số cho mỗi nhịp tim (vốn xuất hiện mỗi 0.8 giây) sẽ gây áp lực rác "
                "bộ nhớ (Garbage Collection) và giật lag nghiêm trọng. Thiết kế Singleton đảm bảo mô hình chỉ được nạp lên RAM một lần duy nhất khi khởi động server, "
                "tái sử dụng bộ nhớ đệm giúp độ trễ suy luận luôn giữ mức ổn định dưới 0.3 miligiây."
            ),
            "transition": "Một kiến trúc tốt phải dựa trên một nền tảng dữ liệu sạch và quy trình thực nghiệm chuẩn tắc. Em xin kính mời Hội đồng xem cách nhóm giải quyết vấn đề Data Leakage tại Slide 07."
        },
        # SLIDE 7
        {
            "num": 7,
            "speaker": "Nguyễn Đào Nam Hải (Team Leader)",
            "title": "Unit 2.2: Chuỗi Xử Lý Dữ Liệu DSP & Kỹ Thuật Triệt Tiêu Data Leakage",
            "unit": "Unit 02 — Project Execution",
            "time": "55 giây (Tích lũy: 5:25)",
            "goal": "Nêu bật tư duy kỹ thuật trung thực và sâu sắc: Phát hiện lỗi rò rỉ dữ liệu (Data Leakage) khi dùng SMOTE trước khi tách tập, chủ động khắc phục bằng Stratified Split trước SMOTE, tạo ra kết quả thực nghiệm trung thực tuyệt đối.",
            "cues": "Chỉ vào biểu đồ so sánh bên phải và hai con số: 97.14% F1 Pan-Tompkins và độ lệch 0.11% giữa Val và Test. Nói với sự tự hào về sự chuẩn mực khoa học.",
            "speech": (
                "Ở slide này, em muốn nhấn mạnh vào hai đóng góp kỹ thuật quan trọng của nhóm trong xử lý dữ liệu:\n\n"
                "Đầu tiên là hiệu năng của chuỗi DSP y sinh. Thuật toán Pan-Tompkins do chúng em cài đặt sử dụng bộ tích phân cửa sổ trượt 150ms "
                "kết hợp ngưỡng kép thích ứng tín hiệu. Khi kiểm thử trên hơn 20.500 nhịp tim thô từ 8 bản ghi PhysioNet khó, thuật toán đạt điểm F1 trung bình "
                "lên tới 97.14%, cá biệt các bản ghi chuẩn như Record 100 đạt 99.98% và Record 200 đạt 99.56%.\n\n"
                "Thứ hai — và đây là bài học kỹ thuật quý giá nhất của chúng em: Khắc phục triệt để lỗi rò rỉ dữ liệu (Data Leakage).\n"
                "Trong các nghiên cứu mở trên Kaggle, nhiều tác giả mắc lỗi áp dụng kỹ thuật cân bằng lớp SMOTE lên toàn bộ tập dữ liệu TRƯỚC KHI chia Validation. "
                "Điều này tạo ra hiện tượng rò rỉ thông tin láng giềng khiến tập Validation đạt độ chính xác ảo lên tới 99.78% nhưng rớt mạnh trên dữ liệu thật.\n\n"
                "Nhóm em đã chủ động bẻ gãy sai lầm này bằng quy trình chuẩn: Tách tập Stratified Validation 10% độc lập hoàn toàn TRƯỚC, sau đó CHỈ áp dụng SMOTE "
                "trên nội bộ tập Train. Kết quả thực nghiệm hoàn toàn minh bạch: Độ chính xác trên tập Validation đạt 98.62%, sát khít với tập Test là 98.51% — "
                "độ lệch chỉ vỏn vẹn 0.11%, chứng minh mô hình có khả năng tổng quát hóa thực chất và không hề bị Overfitting!"
            ),
            "defense": (
                "Q: Tại sao nhóm không chia dữ liệu theo bệnh nhân (Inter-patient) ngay từ đầu mà vẫn chia theo nhịp (Intra-patient)?\n"
                "A: Dạ thưa Hội đồng, đây là một câu hỏi rất sâu sắc về phương pháp luận. Tập dữ liệu chuẩn Kaggle 187 mẫu được cộng đồng tiền xử lý và cắt sẵn "
                "theo từng nhịp nhằm phục vụ benchmark thuật toán nơ-ron tiêu chuẩn AAMI. Nhóm em đã kiểm soát nghiêm ngặt bằng Stratified Split trước SMOTE để đảm bảo "
                "không rò rỉ mẫu tổng hợp. Đồng thời, tại Unit 4 của bài báo cáo hôm nay, nhóm em cũng sẽ công khai thử nghiệm mô hình trên các tập dữ liệu bệnh nhân hoàn toàn mới "
                "(như SVDB, EDB) để đánh giá thực chất hiện tượng Domain Shift liên bệnh nhân."
            ),
            "transition": "Sau khi đã có tập dữ liệu sạch và chuẩn hóa, nhóm tiến hành huấn luyện và đối sánh 5 kiến trúc học sâu. Kính mời Hội đồng cùng quan sát kết quả tại Slide 08."
        },
        # SLIDE 8
        {
            "num": 8,
            "speaker": "Nguyễn Đào Nam Hải (Team Leader)",
            "title": "Unit 2.3: Benchmark 5 Kiến Trúc 1D & Trọng Tâm Lõi ResNet-1D",
            "unit": "Unit 02 — Project Execution",
            "time": "55 giây (Tích lũy: 6:20)",
            "goal": "Chứng minh sự vượt trội của ResNet-1D so với 4 kiến trúc đối sánh (CNN-LSTM, TCN, Mamba, Vanilla 1D-CNN) cả về Accuracy (98.57%), F1-macro (91.70-92.39%), thông lượng (7,546 nhịp/s) và Recall lớp nguy hiểm V (96.20%).",
            "cues": "Chỉ tay vào bảng đối sánh 5 mô hình. Nhấn mạnh vào cấu trúc Residual Block với Skip Connection giúp giải quyết bài toán vanishing gradient.",
            "speech": (
                "Để lựa chọn hạt nhân AI tối ưu nhất cho hệ thống thời gian thực, chúng em không chọn mô hình theo cảm tính mà tiến hành một "
                "thực nghiệm Benchmark toàn diện trên 5 kiến trúc học sâu 1 chiều phổ biến nhất hiện nay: gồm 1D-CNN cơ bản, CNN-LSTM, TCN (Temporal Convolutional Network), "
                "Mamba-1D (State-Space Model mới nhất) và ResNet-1D.\n\n"
                "Kết quả đo lường định lượng trên cùng một tập kiểm thử độc lập cho thấy:\n"
                "• ResNet-1D áp đảo hoàn toàn với Accuracy đạt 98.57% và F1-Macro đạt 91.70% (đo lại đạt 92.39%), bỏ xa CNN-LSTM (85.8%), TCN (82.8%) và Mamba (79.3%).\n"
                "• Về độ trễ suy luận, ResNet-1D chỉ mất 0.134 miligiây cho một nhịp tim, tương đương thông lượng xử lý hơn 7.500 nhịp mỗi giây — cực kỳ lý tưởng cho môi trường streaming đa bệnh nhân.\n"
                "• Đặc biệt về mặt bệnh học tim mạch: Trên nhóm nhịp Ngoại tâm thu thất (Lớp V - PVC) — loại loạn nhịp nguy hiểm nhất có thể dẫn đến rung thất, "
                "ResNet-1D đạt Recall lên tới 96.20% và F1 đạt 95.61%.\n\n"
                "Sức mạnh của mô hình đến từ kiến trúc 3 khối Residual Blocks với các đường tắt Skip Connections, giúp các tầng nơ-ron học sâu trích xuất được "
                "các đặc trưng hình thái biến thiên cục bộ của sóng điện tim mà không bị triệt tiêu đạo hàm."
            ),
            "defense": (
                "Q: Tại sao mô hình Mamba-1D là kiến trúc State-Space rất hiện đại mà kết quả lại thấp nhất trong bảng benchmark (79.3%)?\n"
                "A: Dạ thưa thầy cô, Mamba vốn phát huy sức mạnh vượt trội trên các chuỗi dữ liệu cực kỳ dài (hàng nghìn đến chục nghìn tokens) nhờ cơ chế chọn lọc trạng thái. "
                "Tuy nhiên với một cửa sổ nhịp tim đơn lẻ chỉ có 187 mẫu cục bộ, các liên kết phụ thuộc thời gian là cục bộ chứ không phải khoảng cách xa. "
                "Các bộ lọc tích chập cục bộ kết hợp Skip Connection của ResNet-1D tỏ ra hiệu quả và phù hợp hơn rất nhiều so với cơ chế State-Space trên độ dài chuỗi này."
            ),
            "transition": "Đạt độ chính xác cao là chưa đủ đối với y tế. Làm thế nào để bác sĩ tin tưởng vào quyết định của mô hình? Em xin kính mời Hội đồng chuyển sang Slide 09 với thuật toán 1D Grad-CAM."
        },
        # SLIDE 9
        {
            "num": 9,
            "speaker": "Nguyễn Đào Nam Hải (Team Leader)",
            "title": "Unit 2.4: Explainable AI: 1D Grad-CAM & Cơ Chế Sàng Lọc Rung Nhĩ (AFib)",
            "unit": "Unit 02 — Project Execution",
            "time": "55 giây (Tích lũy: 7:15)",
            "goal": "Giải thích trực quan hóa 1D Grad-CAM kết nối hoàn hảo với giải phẫu học P-QRS-T của tim mạch (chứng minh AI học đúng đặc trưng y khoa chứ không học vẹt nhiễu nền), kết hợp mô-đun phân tích biến thiên Shannon Entropy sàng lọc AFib.",
            "cues": "Dùng laser pointer trỏ vào dải màu nhiệt (heatmap) đỏ rực ở vùng đỉnh QRS và giải thích tương quan giải phẫu học.",
            "speech": (
                "Kính thưa Hội đồng, đây chính là lời giải của NEURO-ECG cho 'Nghịch lý Hộp Đen' trong chẩn đoán y tế: Trí tuệ nhân tạo giải thích được (Explainable AI).\n\n"
                "Chúng em đã phát triển và tích hợp thuật toán 1D Grad-CAM (Gradient-weighted Class Activation Mapping) trực tiếp trên tầng tích chập cuối cùng của ResNet-1D. "
                "Bằng cách tính toán đạo hàm riêng của điểm phân loại đối với từng kênh đặc trưng, hệ thống tạo ra một bản đồ nhiệt 1 chiều mô tả chính xác mức độ kích hoạt của nơ-ron.\n\n"
                "Điều kỳ diệu là bản đồ nhiệt này hoàn toàn tương thích với các tiêu chuẩn hình thái học của Hội Tim mạch Hoa Kỳ:\n"
                "• Khi phát hiện nhịp Ngoại tâm thu thất (PVC - Lớp V), bản đồ nhiệt tập trung hơn 85% năng lượng chú ý vào vùng phức bộ QRS giãn rộng trên 120 miligiây và đoạn sóng T đảo chiều — chính là nơi xảy ra biến dạng bệnh lý.\n"
                "• Khi phát hiện nhịp Ngoại tâm thu nhĩ (PAC - Lớp S), vùng kích hoạt mạnh lập tức dời về phía trước tại vị trí sóng P biến dạng đến sớm.\n"
                "Điều này chứng minh mô hình của chúng em đã thực sự học được bản chất sinh lý học của điện tim chứ không hề học vẹt các nhiễu nền ngẫu nhiên.\n\n"
                "Song song với đó, hệ thống trang bị bộ sàng lọc Rung nhĩ (AFib Screener) đa tầng: phân tích tính bất thường nhịp điệu kéo dài thông qua Shannon Entropy của hiệu khoảng cách dRR, hệ số biến thiên CV_RR và chỉ số pNN50, kích hoạt báo động khi vượt ngưỡng an toàn 0.62."
            ),
            "defense": (
                "Q: Bản đồ nhiệt Grad-CAM có thực sự là căn cứ pháp lý để khẳng định bệnh lý hay không?\n"
                "A: Dạ thưa Hội đồng, chúng em luôn nhấn mạnh: Grad-CAM là công cụ giải thích thuộc tính nơ-ron (Neural Attribution Map), "
                "nó chỉ ra vùng tín hiệu nào khiến mô hình đưa ra quyết định đó. Căn cứ pháp lý chẩn đoán vẫn hoàn toàn dựa trên mắt nhìn và kết luận "
                "của bác sĩ tim mạch; Grad-CAM đóng vai trò 'trợ lý thị giác', hướng sự chú ý của bác sĩ vào đúng vùng bất thường nhanh hơn gấp nhiều lần."
            ),
            "transition": "Để đưa toàn bộ thuật toán tinh vi này từ phòng thí nghiệm ra triển khai trên thiết bị đeo tay IoT, nhóm đã thực hiện bước tối ưu hóa nhúng ra sao? Xin mời Hội đồng nhìn vào Slide 10."
        },
        # SLIDE 10
        {
            "num": 10,
            "speaker": "Nguyễn Đào Nam Hải (Team Leader) -> Handover",
            "title": "Unit 2.5: Tối Ưu Hóa Nhúng: Lượng Tử Hóa ONNX INT8 & Bàn Giao Sân Khấu",
            "unit": "Unit 02 — Project Execution",
            "time": "50 giây (Tích lũy: 8:05)",
            "goal": "Báo cáo thành tích nén 74.5% còn 697.3 KB (đạt KPI < 700 KB của SIC), giải thích cơ chế tăng tốc ONNX FP32 4 lần (0.29ms), và thực hiện bàn giao sân khấu cực kỳ mượt mà, chuyên nghiệp cho bạn Hải Yến sang Unit 3.",
            "cues": "Chỉ tay vào 2 con số ấn tượng: Nén 74.5% và Dung lượng 697.3 KB. Sau khi dứt lời kỹ thuật, xoay người trang trọng, mỉm cười và đưa tay mời bạn Hải Yến.",
            "speech": (
                "Kính thưa Hội đồng, để một giải pháp AI y tế có thể ứng dụng vào đời sống, nó không thể chỉ nằm trên các máy chủ đám mây đắt đỏ, "
                "mà phải chạy được trên các thiết bị đeo tay theo dõi bệnh nhân liên tục (Wearable Edge Devices) với bộ nhớ và pin vô cùng giới hạn.\n\n"
                "Nhóm chúng em đã ứng dụng kỹ thuật lượng tử hóa sau huấn luyện (Post-Training Quantization - PTQ) chuyển đổi mô hình sang định dạng ONNX Runtime INT8. "
                "Và kết quả thu được vô cùng mỹ mãn:\n"
                "• Dung lượng mô hình được nén giảm tới 74.5%, từ 2.735 KB xuống còn đúng 697.3 KB — hoàn thành xuất sắc mục tiêu cam kết ban đầu trong đề cương là dưới 700 KB, "
                "cho phép nạp gọn gàng vào bộ nhớ flash của các dòng vi điều khiển nhúng như ARM Cortex hay Raspberry Pi.\n"
                "• Bảo toàn độ chính xác cao: mô hình chỉ lệch 0.67 điểm % (từ 94.33% xuống 93.66%), hoàn toàn nằm trong dung sai an toàn 2% theo chuẩn y tế.\n"
                "• Trên môi trường CPU chuẩn, phiên bản tối ưu hóa ONNX FP32 đạt độ trễ 0.29 miligiây — tăng tốc gần 4 lần so với runtime PyTorch gốc.\n\n"
                "Như vậy, toàn bộ chuỗi xử lý từ DSP, mô hình AI lõi, thuật toán giải thích Grad-CAM cho tới bộ nén lượng tử hóa ONNX đã được kiểm định kỹ thuật hoàn chỉnh và sẵn sàng vận hành.\n\n"
                "(Lời chuyển giao sân khấu đỉnh cao): Và ngay sau đây, để minh chứng cho năng lực thực tế của toàn bộ kiến trúc này trên nền tảng Web thời gian thực "
                "cùng phiên chạy thử nghiệm trực tiếp, em xin phép được trân trọng nhường lại phần thuyết trình cho bạn Phan Thị Hải Yến để bắt đầu Unit 3: "
                "Kết quả thực nghiệm và phiên Live Demonstration hệ thống NEURO-ECG. Xin trân trọng kính mời bạn Hải Yến!"
            ),
            "defense": (
                "Q: Tại sao trên CPU thông thường, độ trễ đo được của INT8 đôi khi lại chậm hơn FP32?\n"
                "A: Dạ thưa thầy cô, đây là một đặc thù kỹ thuật phần cứng rất kinh điển: Trên các chip CPU thông thường không có tập lệnh tăng tốc phần cứng VNNI hoặc AVX-512 VNNI, "
                "runtime phải mất chi phí chuyển đổi (dequantize/quantize) giữa số nguyên 8-bit và dấu phẩy động. Tuy nhiên, giá trị cốt lõi của INT8 ở đây là nén dung lượng 74.5% xuống 697.3 KB để nhúng vừa flash vi điều khiển; "
                "và khi nạp lên các dòng chip biên chuyên dụng như Jetson Nano hoặc vi xử lý ARM có nhân NEON, INT8 sẽ bộc lộ toàn bộ ưu thế gia tốc vượt trội cả về tốc độ lẫn tiết kiệm điện năng."
            ),
            "transition": "Chuyển giao quyền trình bày cho bạn Phan Thị Hải Yến (Slide 11 đến Slide 18)."
        },
        # SLIDE 11
        {
            "num": 11,
            "speaker": "Phan Thị Hải Yến (Co-presenter)",
            "title": "Unit 3.1: Data & Processing Results: Đo Lường Định Lượng Toàn Diện",
            "unit": "Unit 03 — Results & Demo",
            "time": "55 giây (Tích lũy: 9:00)",
            "goal": "Báo cáo minh bạch kết quả thực nghiệm trên 2 tầng dữ liệu: 21.892 nhịp Kaggle test và 20.546 nhịp WFDB thô từ 8 bản ghi PhysioNet, giải thích trung thực sự phân hóa giữa các lớp nhịp.",
            "cues": "Bước lên vị trí trung tâm, cúi chào Hội đồng nhẹ nhàng, giọng nói rõ ràng, tự tin, mạch lạc.",
            "speech": (
                "Em xin cảm ơn lời giới thiệu của bạn Nam Hải. Kính thưa Hội đồng Giám khảo, em là Phan Thị Hải Yến, sau đây em xin phép được tiếp nối "
                "bài báo cáo với Unit 3: Kết quả thực nghiệm và Phần trình diễn hệ thống thực tế.\n\n"
                "Tại slide này, nhóm chúng em công khai toàn bộ các phép đo định lượng độc lập trên hai môi trường dữ liệu khác nhau:\n"
                "• Thứ nhất, trên tập kiểm thử độc lập Kaggle gồm 21.892 nhịp tim chuẩn hóa: Mô hình đạt Accuracy 98.57% và F1-Macro 92.39%.\n"
                "• Thứ hai, khi đưa vào luồng kiểm thử thực tế từ tín hiệu WFDB thô liên tục trên 8 bản ghi PhysioNet gồm 20.546 nhịp tim: "
                "Hệ thống đạt Accuracy tổng thể 95.18% và F1-Macro đạt 61.80%. Thuật toán phát hiện đỉnh R Pan-Tompkins giữ vững phong độ xuất sắc với F1 trung bình 97.14%.\n\n"
                "Chúng em muốn chỉ ra một điểm bệnh học rất đáng chú ý: Trên nhóm Ngoại tâm thu thất (Lớp V), hệ thống đạt độ nhạy Recall lên tới 97.30%. "
                "Còn đối với nhóm Hợp nhất (Lớp F) và nhóm Chưa phân loại (Lớp Q), do tần suất xuất hiện trong tự nhiên cực kỳ hiếm (lớp Q chỉ có đúng 3 nhịp mẫu trong toàn bộ tập test), "
                "nên điểm F1 trung bình bị kéo giảm. Sự minh bạch này khẳng định nhóm đánh giá dựa trên tiêu chuẩn y sinh khắt khe chứ không tô hồng số liệu tổng thể!"
            ),
            "defense": (
                "Q: Tại sao Accuracy trên tín hiệu thô đạt 95.18% nhưng F1-Macro lại là 61.80%?\n"
                "A: Dạ thưa thầy cô, đây là bài toán mất cân bằng lớp cực kỳ điển hình của dữ liệu y tế thực tế. Nhịp bình thường (Lớp N) chiếm tới hơn 82% tập dữ liệu "
                "và được mô hình nhận diện chính xác gần như tuyệt đối, nên Accuracy tổng thể vẫn rất cao. Tuy nhiên, chỉ số F1-Macro chia đều trọng số cho cả 5 lớp, "
                "và khi các lớp cực hiếm như Q (chỉ có 3 mẫu) hoặc F (chỉ chiếm 0.74%) có ít mẫu để học, điểm số của chúng kéo F1-macro xuống. "
                "Chính vì vậy, trong y tế, chúng em luôn nhìn sâu vào Recall của từng lớp bệnh lý cụ thể (như Recall lớp V đạt 97.30%) chứ không chỉ nhìn vào một con số Accuracy duy nhất."
            ),
            "transition": "Để hiện thực hóa các thuật toán này thành một dịch vụ y tế hoàn chỉnh, kiến trúc backend và bảo mật dữ liệu được xây dựng ra sao? Kính mời Hội đồng cùng xem Slide 12."
        },
        # SLIDE 12
        {
            "num": 12,
            "speaker": "Phan Thị Hải Yến (Co-presenter)",
            "title": "Unit 3.2: Service Implementation: Backend FastAPI & Cơ Sở Dữ Liệu RBAC",
            "unit": "Unit 03 — Results & Demo",
            "time": "50 giây (Tích lũy: 9:50)",
            "goal": "Trình bày hạ tầng dịch vụ Backend FastAPI hiệu năng cao, cơ sở dữ liệu SQLite/SQLAlchemy với phân quyền 3 vai trò và bảng Audit Trail lưu vết trách nhiệm y tế.",
            "cues": "Chỉ tay vào sơ đồ cơ sở dữ liệu và bảng phân quyền RBAC trên slide, nhấn mạnh tính tuân thủ pháp lý y tế.",
            "speech": (
                "Thưa quý Hội đồng, một hệ thống AI y tế chỉ có thể được triển khai khi nó đảm bảo được hai yếu tố: Tính ổn định dịch vụ và Tính toàn vẹn pháp lý.\n\n"
                "Về mặt dịch vụ, Backend của NEURO-ECG được phát triển hoàn toàn trên nền tảng FastAPI bất đồng bộ (Asynchronous Python). "
                "Chúng em áp dụng mẫu thiết kế Singleton Pattern để nạp duy nhất một thực thể mô hình AI và bộ giải thích Grad-CAM vào bộ nhớ, "
                "giúp duy trì luồng truyền phát WebSocket 360Hz mượt mà mà không làm rò rỉ bộ nhớ RAM ngay cả khi streaming liên tục nhiều giờ.\n\n"
                "Về mặt quản trị dữ liệu và pháp lý y tế:\n"
                "• Hệ thống trang bị cơ chế Phân quyền Truy cập theo Vai trò (RBAC) nghiêm ngặt với 3 cấp độ: Bác sĩ (Doctor), Quản trị viên (Admin) và Người quan sát (Viewer).\n"
                "• Đặc biệt, hệ thống sở hữu bảng lưu vết kiểm toán (Audit Trail) chuyên dụng: Mỗi khi bác sĩ xác nhận hoặc điều chỉnh nhãn dự đoán của AI, "
                "toàn bộ thông tin gồm: Mã sự kiện, Nhãn gốc của AI, Nhãn hiệu chỉnh của bác sĩ, Mã định danh người thực hiện và Dấu thời gian chính xác "
                "đều được ghi nhận vĩnh viễn vào cơ sở dữ liệu, đảm bảo tính minh bạch và truy vết trách nhiệm y khoa 100%."
            ),
            "defense": (
                "Q: Hệ thống lưu trữ dữ liệu cục bộ hay đám mây, và có đáp ứng chuẩn bảo mật bệnh án điện tử HIPAA không?\n"
                "A: Dạ thưa Hội đồng, phiên bản Capstone hiện tại sử dụng SQLite với lớp trừu tượng SQLAlchemy ORM, cho phép chuyển đổi sang PostgreSQL trên đám mây "
                "hoặc đặt On-Premise tại máy chủ bệnh viện chỉ bằng 1 dòng cấu hình. Về mặt bảo mật, hệ thống băm mật khẩu chuẩn bcrypt, truyền token JWT xác thực, "
                "và mã hóa liên kết bệnh nhân, tạo tiền đề hoàn hảo để tiến tới chứng chỉ HIPAA ở các giai đoạn sau."
            ),
            "transition": "Tiếp theo, em xin giới thiệu cơ chế hỗ trợ bác sĩ tương tác Human-in-the-loop và hệ thống cảnh báo chuẩn quốc tế tại Slide 13."
        },
        # SLIDE 13
        {
            "num": 13,
            "speaker": "Phan Thị Hải Yến (Co-presenter)",
            "title": "Unit 3.3: Clinical Usability: Human-in-the-Loop & Chuẩn IEC 60601-1-8",
            "unit": "Unit 03 — Results & Demo",
            "time": "50 giây (Tích lũy: 10:40)",
            "goal": "Nêu bật giao diện thân thiện chuẩn phòng mổ, hệ thống cảnh báo 3 cấp độ tuân thủ tiêu chuẩn thiết bị y tế IEC 60601-1-8 và quy trình Human-in-the-loop.",
            "cues": "Nhấn mạnh vào 3 màu cảnh báo: Xanh - Vàng - Đỏ và nút 'Tắt chuông 2 phút' chuẩn phòng cấp cứu.",
            "speech": (
                "Kính thưa Hội đồng, để một phần mềm AI thực sự được các y bác sĩ đón nhận trong môi trường bệnh viện căng thẳng, giao diện phải được "
                "thiết kế theo nguyên lý công thái học y tế (Medical Ergonomics).\n\n"
                "NEURO-ECG áp dụng quy trình tương tác 'Con người trong vòng lặp quyết định' (Human-in-the-loop) với 3 tính năng cốt lõi:\n"
                "1. Hệ thống Báo động Phân tầng Đa mức: Tuân thủ theo tiêu chuẩn an toàn thiết bị y tế IEC 60601-1-8, chia làm 3 cấp độ trực quan: "
                "Màu Xanh (Nhịp bình thường), Màu Vàng (Cảnh báo nhịp chậm/nhịp nhanh hoặc biến thiên nhẹ), và Màu Đỏ khẩn cấp (Phát hiện Ngoại tâm thu thất PVC dày đặc hoặc rung nhĩ).\n"
                "2. Chuông Âm Thanh & Cơ Chế Tắt Âm An Toàn: Khi có sự cố mức Đỏ, chuông báo động tần số cao sẽ vang lên liên tục. Giao diện trang bị nút "
                "'Tắt âm tạm thời 120 giây' (Audio Alarm Pause) — đây là quy chuẩn bắt buộc của máy monitor cấp cứu để tránh gây hoảng loạn cho bệnh nhân và bác sĩ khi đang xử trí.\n"
                "3. Bảng Điều Khiển Soi Chiếu XAI: Bác sĩ chỉ cần nhấp vào một sự kiện cảnh báo, hệ thống lập tức phóng to cửa sổ nhịp tim đó, hiển thị đồng thời "
                "đồ thị sóng và dải màu nhiệt 1D Grad-CAM, giúp bác sĩ đối chiếu hình thái sóng và ký duyệt chẩn đoán chỉ trong vài giây."
            ),
            "defense": (
                "Q: Tiêu chuẩn IEC 60601-1-8 yêu cầu gì và hệ thống của nhóm đã đáp ứng đến mức nào?\n"
                "A: Dạ thưa thầy cô, tiêu chuẩn IEC 60601-1-8 quy định về hệ thống cảnh báo trong thiết bị y tế, yêu cầu phải phân định rõ mức độ ưu tiên bằng màu sắc, "
                "tín hiệu âm thanh ngắt quãng đặc trưng, và có cơ chế tắt âm tạm thời có đếm ngược thời gian để bác sĩ thao tác. Hệ thống của chúng em đã cài đặt đầy đủ "
                "các quy chuẩn giao diện này (3 màu đèn flash, chuông audio Web Audio API, và đếm ngược 120s mute an toàn), sẵn sàng cho các bài kiểm định phần mềm y tế."
            ),
            "transition": "Và bây giờ, không để quý Hội đồng phải chờ đợi lâu hơn nữa, em xin phép bước vào Slide 14 — Phiên Live Demonstration trực tiếp hệ thống NEURO-ECG!"
        },
        # SLIDE 14
        {
            "num": 14,
            "speaker": "Phan Thị Hải Yến (Điều hành Demo) & Nam Hải (Hỗ trợ kỹ thuật)",
            "title": "Unit 3.4 & 3.5: Testing & Live Demo: 42/42 Tests Pass & Kịch Bản 5 Pha",
            "unit": "Unit 03 — Results & Demo",
            "time": "150 giây (2.5 phút) (Tích lũy: 13:10)",
            "goal": "Thực hiện phiên Live Demo 5 pha mượt mà trên hệ thống chạy thật, chứng minh toàn bộ 42/42 bài kiểm thử tự động CI/CD đạt 100%, ghi điểm tuyệt đối về tính hoàn chỉnh của sản phẩm.",
            "cues": "Chuyển màn hình sang trình duyệt web đang chạy ứng dụng thực tế trên localhost:3000 hoặc IP máy chủ. Thao tác dứt khoát, giọng thuyết minh từng bước rõ ràng.",
            "speech": (
                "Kính thưa quý Hội đồng, trước khi bắt đầu phiên Live Demo, em xin trân trọng thông báo: Toàn bộ hệ thống NEURO-ECG đã vượt qua bộ kiểm thử tự động "
                "gồm 42 bài tests: 41 bài Pytest kiểm tra backend DSP, API, WebSocket và 1 bài kiểm thử giao diện Vitest — tất cả đều đạt kết quả Pass 100% trên pipeline CI/CD GitHub Actions.\n\n"
                "Và sau đây, em xin phép mời Hội đồng cùng hướng mắt lên màn hình theo dõi 5 Pha Demo thực tế của hệ thống:\n\n"
                "• PHA 1: KHỞI TẠO & CHỌN HỒ SƠ BỆNH NHÂN (00:00 - 00:25)\n"
                "Em đăng nhập vào hệ thống với vai trò Bác sĩ Chuyên khoa (Doctor). Tại danh sách hồ sơ, em chọn Bệnh nhân mang mã bệnh án gắn với bản ghi MIT-BIH Record 208 — "
                "đây là một ca bệnh điển hình có tần suất xuất hiện các nhịp Ngoại tâm thu thất (PVC) và nhịp bộ nối rất phức tạp.\n\n"
                "• PHA 2: GIÁM SÁT SÓNG ĐIỆN TIM THỜI GIAN THỰC 360Hz (00:25 - 00:55)\n"
                "Em nhấn nút 'Bắt Đầu Giám Sát'. Ngay lập tức, luồng dữ liệu 2 kênh thô gồm Lead MLII và Lead V1 được WebSocket truyền phát trực tiếp lên màn hình "
                "với tốc độ 60 khung hình/giây. Đồ thị vẽ mượt mà, đỉnh R được thuật toán Pan-Tompkins đánh dấu bằng chấm tròn xanh ngay lập tức. "
                "Các chỉ số sinh tồn như Nhịp tim (BPM) và Độ biến thiên nhịp tim (HRV) được cập nhật liên tục theo từng nhịp.\n\n"
                "• PHA 3: KÍCH HOẠT CẢNH BÁO BỆNH LÝ & TẮT ÂM IEC 60601-1-8 (00:55 - 01:25)\n"
                "Quý thầy cô có thể thấy, ngay khi một nhịp Ngoại tâm thu thất (PVC) xuất hiện, hệ thống lập tức phát hiện trong 0.13 miligiây! "
                "Thẻ cảnh báo chuyển sang màu Đỏ khẩn cấp, biểu tượng nhịp đập chuyển sang màu đỏ và chuông báo động âm thanh vang lên. "
                "Để xử trí, em bấm nút 'Tắt chuông 2 phút' — âm thanh dừng ngay lập tức và đồng hồ đếm ngược 120 giây xuất hiện trên góc phải màn hình, "
                "đúng theo tiêu chuẩn phòng cấp cứu IEC 60601-1-8.\n\n"
                "• PHA 4: SOI CHIẾU BẢN ĐỒ NHIỆT GRAD-CAM & DUYỆT NHÃN HUMAN-IN-THE-LOOP (01:25 - 02:05)\n"
                "Tiếp theo, em chuyển sang tab 'Phân Tích XAI'. Em bấm chọn sự kiện loạn nhịp vừa xảy ra. Cửa sổ 187 mẫu của nhịp tim đó lập tức được hiển thị "
                "kèm theo bản đồ nhiệt 1D Grad-CAM bên dưới. Thầy cô có thể thấy dải màu đỏ rực tập trung chính xác vào phức bộ QRS giãn rộng 140ms. "
                "Độ tin cậy của AI là 96.6%. Với tư cách Bác sĩ, em nhấn nút 'Xác Nhận Nhãn PVC' — hệ thống phản hồi thành công và một dòng lịch sử kiểm toán "
                "lập tức được ghi vào bảng Audit Trail với tên bác sĩ và timestamp chính xác.\n\n"
                "• PHA 5: TẢI FILE DỮ LIỆU NGOÀI & XUẤT BÁO CÁO Y TẾ (02:05 - 02:30)\n"
                "Cuối cùng, em thao tác tải lên một tệp CSV điện tim ngoài bất kỳ (30 giây bản ghi 360Hz). Hệ thống chỉ mất 1.2 giây để phân tích toàn bộ "
                "và xuất ra một bản báo cáo y tế dạng PDF chuẩn chỉnh, có đầy đủ biểu đồ sóng, thống kê phân bố nhịp và chữ ký xác nhận của bác sĩ!"
            ),
            "defense": (
                "Q: Nếu tín hiệu truyền qua WebSocket bị rớt mạng hoặc gián đoạn thì hệ thống xử lý ra sao?\n"
                "A: Dạ thưa Hội đồng, giao diện React của chúng em tích hợp cơ chế tự động kết nối lại (Auto-Reconnect với Exponential Backoff). "
                "Đồng thời, tại tầng backend, chúng em duy trì một bộ đệm vòng (Ring Buffer) 1.000 mẫu gần nhất; khi mạng phục hồi, "
                "các gói tin bị gián đoạn sẽ được đồng bộ lại ngay lập tức mà không làm mất dấu các sự kiện loạn nhịp của bệnh nhân."
            ),
            "transition": "Sau phiên trình diễn thực tế, em xin kính mời Hội đồng quay lại bài báo cáo để đánh giá những tác động lâm sàng và giá trị thực tiễn tại Slide 15."
        },
        # SLIDE 15
        {
            "num": 15,
            "speaker": "Phan Thị Hải Yến (Co-presenter)",
            "title": "Unit 4.1: Accomplishments & Clinical Benefits: Thành Tựu & Tác Động Thực Tiễn",
            "unit": "Unit 04 — Projected Impact",
            "time": "45 giây (Tích lũy: 13:55)",
            "goal": "Khái quát 3 thành tựu kỹ thuật lớn nhất đã đạt được và định lượng giá trị kinh tế - xã hội đối với ngành y tế và cộng đồng bệnh nhân.",
            "cues": "Nói với sự tự tin và niềm tự hào về ý nghĩa xã hội của đề tài kỹ thuật.",
            "speech": (
                "Kính thưa Hội đồng, nhìn lại chặng đường nghiên cứu, NEURO-ECG đã hoàn thành xuất sắc 3 thành tựu kỹ thuật mang tính đột phá:\n"
                "1. Chúng em đã xây dựng thành công một chuỗi tích hợp trọn vẹn từ đầu đến cuối (End-to-End Clinical Pipeline) — kết nối từ việc lọc tín hiệu y sinh thô, "
                "phát hiện đỉnh R với F1 97.14%, suy luận ResNet-1D trong 0.13 miligiây, cho tới một ứng dụng Web lâm sàng tương tác thời gian thực.\n"
                "2. Xóa bỏ hoàn toàn rào cản Hộp Đen trong chẩn đoán AI y tế bằng giải thuật 1D Grad-CAM, trao quyền cho bác sĩ soi chiếu trực quan và lưu vết pháp lý qua Audit Trail.\n"
                "3. Hoàn thành mục tiêu đề cương với mô hình nén ONNX INT8 dưới 700 KB, sẵn sàng cho kỷ nguyên thiết bị theo dõi sức khỏe đeo tay Edge Wearable.\n\n"
                "Về mặt tác động lâm sàng và xã hội: NEURO-ECG giúp giải phóng hơn 80% thời gian đọc bản ghi thủ công cho bác sĩ tim mạch, "
                "hạ thấp tỷ lệ bỏ sót các cơn loạn nhịp kịch phát nguy hiểm, đồng thời mở ra cơ hội đưa công nghệ tầm soát tim mạch chất lượng cao "
                "về tận các trạm y tế vùng sâu vùng xa với chi phí phần cứng cực kỳ tiết kiệm."
            ),
            "defense": (
                "Q: Dự án đã đo lường thực tế mức độ giảm tải 80% thời gian của bác sĩ hay chưa?\n"
                "A: Dạ thưa thầy cô, con số 80% là mục tiêu tiềm năng dựa trên các nghiên cứu lâm sàng về hệ thống CDSS trên thế giới (khi AI tự động đánh dấu "
                "và gom cụm 90% nhịp bình thường, bác sĩ chỉ cần tập trung thẩm định 10% nhịp bất thường nghi ngờ). Nhóm chúng em đã tích hợp sẵn cơ chế đếm thời gian duyệt "
                "trong bảng Audit Trail để chuẩn bị cho giai đoạn thử nghiệm lâm sàng thực tế tiếp theo."
            ),
            "transition": "Bên cạnh những kết quả đạt được, một nghiên cứu khoa học chân chính luôn cần sự trung thực về những mặt hạn chế. Em xin trình bày chi tiết tại Slide 16."
        },
        # SLIDE 16
        {
            "num": 16,
            "speaker": "Phan Thị Hải Yến (Co-presenter)",
            "title": "Unit 4.2: Future Improvements & Technical Limitations: Đánh Giá Trung Thực",
            "unit": "Unit 04 — Projected Impact",
            "time": "50 giây (Tích lũy: 14:45)",
            "goal": "Thể hiện thái độ khoa học nghiêm túc, thẳng thắn mổ xẻ hiện tượng Domain Shift (suy giảm Recall S/F khi thử nghiệm trên cơ sở dữ liệu ngoài SVDB, EDB) và đề xuất giải pháp kỹ thuật cụ thể.",
            "cues": "Giọng nói điềm tĩnh, khoa học, chỉ vào biểu đồ kiểm định đa nguồn trên màn chiếu.",
            "speech": (
                "Kính thưa Hội đồng, với tinh thần nghiên cứu học thuật nghiêm túc và cầu thị, nhóm chúng em thẳng thắn công khai những hạn chế kỹ thuật hiện tại:\n\n"
                "Thách thức lớn nhất mà nhóm phát hiện là 'Hiện tượng Dịch chuyển Miền dữ liệu' (Domain Shift) khi đem mô hình huấn luyện trên MIT-BIH đi kiểm thử ngoại kiểm "
                "trên các bộ cơ sở dữ liệu độc lập khác:\n"
                "• Trên tập nhịp Ngoại tâm thu nhĩ (Lớp S), Recall bị giảm xuống còn 0.4% trên cơ sở dữ liệu SVDB và 3.6% trên EDB, trong khi lớp Ngoại tâm thu thất (Lớp V) vẫn duy trì độ chính xác cao.\n"
                "• Qua phân tích chuyên sâu, chúng em phát hiện nguyên nhân đến từ: Sự khác biệt về vị trí dán điện cực (đạo trình MLII so với Lead II/V5 chuẩn), "
                "sự khác nhau về đặc tính phần cứng máy ghi tín hiệu giữa các bệnh viện, và sự mất cân bằng cực đoan của nhịp S trong các bộ dữ liệu ngoài.\n\n"
                "Giải pháp mà nhóm đã thử nghiệm thành công là: Khi tiến hành kỹ thuật tinh chỉnh (Fine-tuning) thích nghi miền trên tập dữ liệu INCART, "
                "độ chính xác tổng thể lập tức tăng vọt từ 85.94% lên 93.18%. Điều này khẳng định hướng đi dài hạn của dự án là áp dụng kỹ thuật Học thích nghi đa miền "
                "(Domain Adaptation) và huấn luyện trên dữ liệu tổng hợp đa trung tâm."
            ),
            "defense": (
                "Q: Tại sao nhóm không dùng kỹ thuật Cross-Validation liên bệnh nhân (Inter-patient) ngay từ đầu để tránh Domain Shift?\n"
                "A: Dạ thưa Hội đồng, đây là một câu hỏi rất trúng bản chất! Trong phạm vi thời gian 6 tuần của Capstone SIC, mục tiêu hàng đầu của nhóm là xây dựng "
                "một đường ống hoàn chỉnh End-to-End từ DSP, AI, XAI đến Full-stack Web. Nhóm đã áp dụng Stratified Split trước SMOTE để đảm bảo hoàn toàn không bị rò rỉ dữ liệu. "
                "Và việc chủ động chạy thử nghiệm trên SVDB, EDB và INCART để công khai hiện tượng Domain Shift hôm nay chính là bằng chứng cho thấy nhóm hoàn toàn nắm vững "
                "bản chất y sinh và đã xác định rõ bài toán cần giải quyết ở giai đoạn tiếp theo."
            ),
            "transition": "Từ những bài học quý báu đó, nhóm đã đúc kết được những kinh nghiệm gì và vạch ra lộ trình phát triển ra sao? Kính mời Hội đồng cùng nhìn vào Slide 17."
        },
        # SLIDE 17
        {
            "num": 17,
            "speaker": "Phan Thị Hải Yến (Co-presenter)",
            "title": "Unit 5.1: Team Member Review & 3-Phase Roadmap: Tự Đánh Giá & Lộ Trình",
            "unit": "Unit 05 — Team Review",
            "time": "45 giây (Tích lũy: 15:30)",
            "goal": "Tự đánh giá năng lực và sự trưởng thành của 2 thành viên Nam Hải & Hải Yến qua chương trình SIC, đồng thời trình bày lộ trình 3 giai đoạn hướng tới thương mại hóa thiết bị y tế SaMD.",
            "cues": "Ánh mắt ấm áp, hướng về bạn đồng hành Nam Hải và hướng về Ban Giảng viên SIC với sự tri ân.",
            "speech": (
                "Kính thưa thầy cô, trải qua 6 tuần thực chiến đầy thử thách của chương trình Samsung Innovation Campus, cả hai chúng em đều đã có những bước trưởng thành vượt bậc:\n"
                "• Với bạn Nam Hải, bài học lớn nhất là năng lực kết nối nhịp nhàng giữa mô hình AI lý thuyết với kiến trúc dịch vụ thực tế, kỹ năng làm chủ lượng tử hóa ONNX "
                "và quản lý chặt chẽ phiên bản trọng số để mọi kết quả nghiên cứu đều có thể truy vết độc lập.\n"
                "• Với bản thân em (Hải Yến), em đã rèn luyện được tư duy y sinh sâu sắc: thấu hiểu rằng trong dữ liệu y tế, một con số Accuracy 98% sẽ trở nên vô nghĩa nếu "
                "chúng ta không bảo vệ được các lớp bệnh lý hiếm; và bài học phát hiện, sửa lỗi Data Leakage sẽ là hành trang khoa học vô giá đối với em.\n\n"
                "Về tương lai của dự án, nhóm đã xác lập một Lộ trình 3 Giai đoạn rõ ràng:\n"
                "• Giai đoạn 1 (Ngắn hạn - 3 tháng): Hoàn thiện đồng bộ ID bệnh nhân đa phiên, hợp nhất công thức tính Rung nhĩ và chuẩn hóa xuất báo cáo PDF tự động.\n"
                "• Giai đoạn 2 (Trung hạn - 6 tháng): Tích hợp trực tiếp với mạch cảm biến phần cứng IoT ECG (AD8232 / MAX30003) giao tiếp vi điều khiển ESP32 và nạp mô hình ONNX INT8 lên Raspberry Pi.\n"
                "• Giai đoạn 3 (Dài hạn - 12 tháng): Tiến hành thử nghiệm lâm sàng mù đôi tại bệnh viện và đăng ký chứng nhận Phần mềm Thiết bị Y tế (SaMD)."
            ),
            "defense": (
                "Q: Khả năng thương mại hóa thực tế của dự án này ở thị trường Việt Nam ra sao?\n"
                "A: Dạ thưa Hội đồng, các dòng máy Holter ECG nhập ngoại hiện nay có giá từ vài trăm triệu đến hàng tỷ đồng và phần mềm phân tích đi kèm rất đắt đỏ, "
                "không có tính năng giải thích Grad-CAM bằng tiếng Việt. Giải pháp của NEURO-ECG hướng tới mô hình SaaS hoặc đóng gói phần cứng chi phí thấp dưới 2 triệu đồng, "
                "hoàn toàn có thể trang bị đại trà cho các phòng khám gia đình và trung tâm y tế tuyến huyện."
            ),
            "transition": "Và sau đây, nhóm chúng em xin được chuyển sang slide cuối cùng để tổng kết lại toàn bộ đề tài bảo vệ ngày hôm nay."
        },
        # SLIDE 18
        {
            "num": 18,
            "speaker": "Hải Yến & Nam Hải (Cùng chào kết luận)",
            "title": "Unit 5.2: Conclusion, Acknowledgments & Q&A Defense: Kết Luận & Cảm Ơn",
            "unit": "Unit 05 — Team Review",
            "time": "30 giây (Tích lũy: 16:00)",
            "goal": "Tổng kết đanh thép các thành tựu then chốt, gửi lời tri ân chân thành tới Ban Giảng viên SIC, ĐHBK Hà Nội và Tập đoàn Samsung, mở đầu phiên hỏi đáp phản biện.",
            "cues": "Cả hai bạn Nam Hải và Hải Yến cùng đứng sóng đôi trang trọng, mỉm cười, cúi đầu chào sâu Hội đồng.",
            "speech": (
                "(Hải Yến): Kính thưa quý thầy cô trong Hội đồng Giám khảo, để khép lại bài báo cáo hôm nay, nhóm chúng em xin được đọng lại bằng 3 thông điệp kỹ thuật cốt lõi: "
                "NEURO-ECG đã chứng minh được tính Chính Xác (98.57% test accuracy), tính Minh Bạch (1D Grad-CAM bảo vệ quyết định bác sĩ) và tính Khả Thi Nhúng (ONNX INT8 dưới 700 KB).\n\n"
                "(Nam Hải tiếp lời): Chúng em xin được bày tỏ lòng biết ơn sâu sắc nhất tới Ban Giảng viên Chương trình Samsung Innovation Campus 2026, "
                "các Thầy Cô giáo Đại học Bách khoa Hà Nội và Tập đoàn Điện tử Samsung đã tận tình giảng dạy, truyền cảm hứng và đồng hành cùng chúng em trong suốt khóa học vừa qua.\n\n"
                "(Cả hai cùng nói): Nhóm chúng em xin chân thành cảm ơn quý Hội đồng đã chú ý lắng nghe, và chúng em rất mong nhận được những câu hỏi, "
                "góp ý quý báu của các Thầy Cô trong phiên hỏi đáp phản biện ngay sau đây!"
            ),
            "defense": (
                "Q: Tinh thần sẵn sàng phản biện của nhóm thế nào?\n"
                "A: Dạ chúng em đã chuẩn bị sẵn sàng toàn bộ mã nguồn trên GitHub, dashboard demo trực tiếp, các bảng số liệu thực nghiệm đo đạc và tài liệu minh chứng, "
                "rất mong được lắng nghe câu hỏi từ quý Thầy Cô ạ!"
            ),
            "transition": "Mở đầu phiên hỏi đáp phản biện Q&A với Hội đồng Giám khảo."
        }
    ]

    for item in slides:
        p_head = doc.add_paragraph()
        p_head.paragraph_format.space_before = Pt(14)
        p_head.paragraph_format.space_after = Pt(2)
        r_head = p_head.add_run(f"SLIDE {item['num']:02d}: {item['title'].upper()}")
        r_head.font.name = 'Calibri'
        r_head.font.size = Pt(13)
        r_head.font.bold = True
        r_head.font.color.rgb = NAVY
        
        tbl = doc.add_table(rows=4, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        info = [
            ("Người trình bày:", item['speaker']),
            ("Phân mục & Thời lượng:", f"{item['unit']}  |  Mục tiêu: {item['time']}"),
            ("Mục tiêu & Thông điệp:", item['goal']),
            ("Phong thái & Cử chỉ sân khấu:", item['cues'])
        ]
        for row_i, (k, v) in enumerate(info):
            c0, c1 = tbl.rows[row_i].cells[0], tbl.rows[row_i].cells[1]
            c0.width = Inches(2.2)
            c1.width = Inches(4.6)
            set_cell_background(c0, "F8F9FA")
            set_cell_background(c1, "FFFFFF")
            set_cell_margins(c0, top=50, bottom=50, left=80, right=80)
            set_cell_margins(c1, top=50, bottom=50, left=80, right=80)
            
            p0 = c0.paragraphs[0]
            r0 = p0.add_run(k)
            r0.font.bold = True
            r0.font.size = Pt(9.5)
            r0.font.color.rgb = NAVY
            
            p1 = c1.paragraphs[0]
            r1 = p1.add_run(v)
            r1.font.size = Pt(9.5)
            r1.font.color.rgb = DARK
            
        add_callout(
            doc,
            f"LỜI THOẠI THUYẾT TRÌNH CHI TIẾT (SPEAKER SCRIPT — SLIDE {item['num']:02d})",
            item['speech'],
            bg_hex="F4F9FD",
            border_hex="0072CE"
        )
        
        add_callout(
            doc,
            f"CHIẾN THUẬT PHẢN BIỆN NHANH (Q&A FAST DEFENSE — SLIDE {item['num']:02d})",
            item['defense'],
            bg_hex="FFFDF5",
            border_hex="D97706"
        )
        
        p_tr = doc.add_paragraph()
        p_tr.paragraph_format.space_before = Pt(2)
        p_tr.paragraph_format.space_after = Pt(8)
        r_tr_lbl = p_tr.add_run("➔ Câu nối chuyển tiếp (Transition Bridge): ")
        r_tr_lbl.font.bold = True
        r_tr_lbl.font.size = Pt(10)
        r_tr_lbl.font.color.rgb = GREEN
        r_tr_txt = p_tr.add_run(f'"{item["transition"]}"')
        r_tr_txt.font.italic = True
        r_tr_txt.font.size = Pt(10)
        r_tr_txt.font.color.rgb = DARK

    # CHEAT SHEET
    doc.add_page_break()
    p_sum_title = doc.add_paragraph()
    p_sum_title.paragraph_format.space_before = Pt(10)
    p_sum_title.paragraph_format.space_after = Pt(4)
    r_sum_t = p_sum_title.add_run("BẢNG TỔNG HỢP 'THẦN CHÚ' PHẢN BIỆN TOÀN DIỆN CHO CẢ HAI BẠN")
    r_sum_t.font.name = 'Calibri'
    r_sum_t.font.size = Pt(15)
    r_sum_t.font.bold = True
    r_sum_t.font.color.rgb = NAVY
    
    cheat_items = [
        ("1. 'Tại sao dùng 1D mà không chuyển sang 2D Spectrogram?'",
         "Tín hiệu điện tim bản chất là chuỗi thời gian 1 chiều với các điểm uốn sinh lý cực kỳ sắc nét. Mô hình 1D xử lý trực tiếp tín hiệu thô, giữ trọn vẹn pha và biên độ biên đạo cực đại, không phát sinh chi phí tính toán biến đổi Fourier (STFT), giảm thiểu bộ nhớ và đạt độ trễ chỉ 0.13ms so với hàng chục miligiây của các mạng 2D nặng nề."),
        ("2. 'Độ chính xác 98.57% có đáng tin cậy không khi dữ liệu mất cân bằng nặng?'",
         "Nhóm em hoàn toàn không chỉ nhìn vào Accuracy! Trên tập test thực tế, lớp F chỉ chiếm 0.74% trong khi lớp N chiếm hơn 82%. Vì vậy, nhóm luôn đối chiếu chỉ số F1-Macro đạt 92.39%, đặc biệt trên lớp rối loạn nhịp nguy hiểm nhất là Ngoại tâm thu thất (PVC - Lớp V), mô hình đạt Recall 96.20% và F1 95.61%."),
        ("3. 'Data Leakage được xử lý triệt để như thế nào?'",
         "Nhóm đã phát hiện và loại bỏ lỗi phổ biến trong cộng đồng: tuyệt đối KHÔNG áp dụng SMOTE trước khi chia tập. Nhóm thực hiện Stratified Split 10% Validation trước, sau đó chỉ cân bằng trên nội bộ tập Train. Bằng chứng thực nghiệm là độ lệch giữa Validation (98.62%) và Test (98.51%) chỉ là 0.11%, chứng minh mô hình không hề overfit."),
        ("4. 'Grad-CAM có đảm bảo tính đúng đắn y khoa không?'",
         "Grad-CAM là bản đồ thuộc tính gradient nơ-ron chứng minh mô hình kích hoạt tập trung > 85% năng lượng vào đúng phức bộ QRS giãn rộng và sóng T đối với nhịp V, sóng P đối với nhịp S. Đây là bằng chứng cho thấy mạng nơ-ron học đúng đặc trưng giải phẫu học chứ không phán đoán dựa vào nhiễu đường nền."),
        ("5. 'Lợi ích thực tế của việc lượng tử hóa ONNX INT8?'",
         "Dung lượng mô hình giảm 74.5% xuống 697.3 KB, hoàn thành mục tiêu dưới 700 KB để nạp vào bộ nhớ flash của các chip đeo tay Wearable. Trên CPU chuẩn, bản ONNX FP32 tăng tốc 4 lần (0.29ms); còn bản INT8 sẵn sàng khai phóng toàn bộ tốc độ xử lý khi chạy trên các dòng chip biên có tập lệnh VNNI hoặc ARM NEON."),
        ("6. 'Tại sao F1 trên tín hiệu thô WFDB lại là 61.80%?'",
         "Do lớp Q chỉ có đúng 3 mẫu trong 20.546 nhịp tim và F chỉ chiếm tỷ lệ nhỏ; việc chia đều F1-macro cho 5 lớp làm giảm điểm trung bình. Tuy nhiên, trên lớp bệnh lý sống còn là PVC (Lớp V), hệ thống đạt Recall 97.30%, và thuật toán Pan-Tompkins đạt F1 phát hiện đỉnh R 97.14%."),
        ("7. 'Hệ thống đã loại trừ trách nhiệm pháp lý của bác sĩ chưa?'",
         "NEURO-ECG định vị là CDSS (Hệ thống hỗ trợ ra quyết định lâm sàng), mọi chẩn đoán cuối cùng thuộc về bác sĩ. Bảng Audit Trail lưu vết định danh, nhãn sửa và timestamp giúp minh bạch hóa trách nhiệm và làm dữ liệu tinh chỉnh mô hình sau này.")
    ]
    
    for q_idx, (q_txt, a_txt) in enumerate(cheat_items):
        add_callout(
            doc,
            f"VŨ KHÍ PHẢN BIỆN {q_idx+1}: {q_txt}",
            a_txt,
            bg_hex="F7FAFC",
            border_hex="0A2540"
        )
        
    out_docx = r"docs/Kich_ban_Thuyet_trinh_Chi_tiet_Toan_bo_18_Slide_NEURO_ECG.docx"
    doc.save(out_docx)
    print(f"Successfully generated full 18-slide presentation script at: {out_docx}")

if __name__ == "__main__":
    build_full_script()
