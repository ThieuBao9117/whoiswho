/**
 * getInitialsAvatar - Tạo URL avatar chữ cái đầu Họ + Tên
 * Ví dụ: "Trần Minh Trí" -> "TT"
 *         "Kim Chang-heon" -> "KC"
 */
export function getInitials(fullName = '') {
  const words = fullName.trim().split(/\s+/).filter(Boolean);
  if (words.length === 0) return 'NV';
  if (words.length === 1) return words[0][0].toUpperCase();
  // Lấy chữ cái đầu từ word ĐẦU TIÊN và word CUỐI CÙNG
  return (words[0][0] + words[words.length - 1][0]).toUpperCase();
}

// Bảng màu đẹp cho avatar chữ cái
const AVATAR_COLORS = [
  '4F46E5', // indigo
  '7C3AED', // violet
  'DB2777', // pink
  'DC2626', // red
  'D97706', // amber
  '059669', // emerald
  '0284C7', // sky
  '7C3AED', // purple
  'EA580C', // orange
  '0891B2', // cyan
];

function colorFromName(name = '') {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}

/**
 * getAvatarUrl - Trả về URL avatar hợp lệ
 * - Nếu có photo (URL tuyệt đối hoặc tương đối từ HRM): dùng photo
 * - Nếu không: tạo avatar chữ cái đầu
 * 
 * @param {string} photo - URL ảnh từ backend
 * @param {string} fullName - Họ tên đầy đủ
 * @param {string} hrmDomain - Domain HRM (mặc định hrm.csbrg.com)
 */
export function getAvatarUrl(photo, fullName, hrmDomain = 'http://hrm.csbrg.com') {
  if (photo && photo.trim()) {
    // Nếu là relative URL, thêm domain HRM
    if (photo.startsWith('/')) return `${hrmDomain}${photo}`;
    return photo;
  }
  // Không có ảnh → dùng chữ cái đầu
  const initials = getInitials(fullName);
  const bg = colorFromName(fullName);
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(initials)}&background=${bg}&color=fff&size=200&bold=true&format=svg`;
}
