function startVoiceInput() {
    if (!('webkitSpeechRecognition' in window)) { alert("Mic not supported"); return; }
    var rec = new webkitSpeechRecognition();
    rec.lang = "en-US";
    rec.onresult = function(evt) {
        document.getElementById('input').value = evt.results[0][0].transcript;
    };
    rec.start();
}
