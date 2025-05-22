export function getUserIdFromToken() {
    const token = localStorage.getItem('access_token');
    if (!token) return null;
  
    try {
      const payloadBase64 = token.split('.')[1];
      const payloadJson = atob(payloadBase64);
      const payload = JSON.parse(payloadJson);
  
      return payload.sub || null; // по умолчанию identity мапится в sub
    } catch (error) {
      console.error('Ошибка при декодировании токена:', error);
      return null;
    }
  }
  