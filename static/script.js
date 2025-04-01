// filepath: c:\KNOU_HJH\softwareContest\softwareContest\static\script.js
function stopBlinking() {
    const blinkingText = document.getElementById('blinking-text');
    blinkingText.classList.remove('blink');
}

function startBlinking() {
    const blinkingText = document.getElementById('blinking-text');
    blinkingText.classList.add('blink');
}
