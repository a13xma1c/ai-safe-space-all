// Simple floating emoji mood wheel
document.addEventListener("DOMContentLoaded", function() {
    let moods = ["😀","🙂","😐","🙁","😭"];
    let wheel = document.createElement("div");
    wheel.style.position = "fixed"; wheel.style.bottom="16px"; wheel.style.right="16px"; wheel.style.zIndex="999";
    wheel.innerHTML = moods.map(m=>`<span style="font-size:2em;cursor:pointer;margin:2px">${m}</span>`).join('');
    wheel.onclick = (e) => {
        if (e.target.textContent) {
            localStorage.setItem("mood_today", e.target.textContent);
            alert("Your mood is logged (privately, only for you): "+e.target.textContent);
        }
    };
    document.body.appendChild(wheel);
});
