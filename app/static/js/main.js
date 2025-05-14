// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', () => {
    // 현재 시간 표시
    const updateTime = () => {
        const now = new Date();
        const timeString = now.toLocaleString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
        document.querySelector('footer').innerHTML = 
            `<p>&copy; 2024 Honken Mini Hub | Last Updated: ${timeString}</p>`;
    };

    // 초기 시간 표시
    updateTime();
    // 1초마다 시간 업데이트
    setInterval(updateTime, 1000);
}); 