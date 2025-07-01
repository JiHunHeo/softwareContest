// filepath: c:\KNOU_HJH\softwareContest\softwareContest\static\script.js
function stopBlinking() {
    const blinkingText = document.getElementById('blinking-text');
    blinkingText.classList.remove('blink');
}

function startBlinking() {
    const blinkingText = document.getElementById('blinking-text');
    blinkingText.classList.add('blink');
}

/** index.html에 텍스트 추가하기 */
function missionCompleteDate() {
    let today = new Date();
    document.getElementById('github-mission-C-list').innerHTML =
        today.getFullYear().toString().substring(2, 4) + '년 ' + (today.getMonth() + 1) + '월 ' + today.getDate() + '일 ' + '기준 작업자 명단 ^^';
}
missionCompleteDate();
