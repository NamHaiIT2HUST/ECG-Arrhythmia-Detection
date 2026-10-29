import regularFont from '../assets/fonts/DejaVuSans.ttf?inline';
import boldFont from '../assets/fonts/DejaVuSans-Bold.ttf?inline';
import italicFont from '../assets/fonts/DejaVuSans-Oblique.ttf?inline';

export const PDF_FONT_FAMILY = 'DejaVuSans';

// Nhúng TTF vào PDF để tiếng Việt hiển thị đúng trên mọi máy, kể cả khi offline.
// Module này chỉ được tải khi người dùng xuất PDF.
export const registerPDFFonts = (doc) => {
  const fonts = [
    ['DejaVuSans.ttf', regularFont, 'normal'],
    ['DejaVuSans-Bold.ttf', boldFont, 'bold'],
    ['DejaVuSans-Oblique.ttf', italicFont, 'italic'],
  ];

  for (const [filename, dataUrl, style] of fonts) {
    doc.addFileToVFS(filename, dataUrl.slice(dataUrl.indexOf(',') + 1));
    doc.addFont(filename, PDF_FONT_FAMILY, style);
  }
};
