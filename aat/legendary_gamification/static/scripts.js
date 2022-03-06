var timer = new easytimer.Timer();
const timeBar = document.querySelector(".time-bar")
const timeBarRed = document.getElementsByClassName("red-bar")[0]
const timeBarWhite = document.getElementsByClassName("white-bar")[0]

timer.start({precision: 'seconds', startValues: {seconds: 0}, target: {seconds: 10}})

timer.addEventListener('secondsUpdated', function(e) {
    timeBarRed.style.flex =  timer.getTimeValues().seconds * 0.2;
    // timeBarWhite.style.flex = (10 - timer.getTimeValues().seconds) * 0.2
    console.log(timer.getTotalTimeValues().seconds)
    if (timer.getTimeValues().seconds >= 7 && timer.getTimeValues().seconds < 10) {
        timeBarRed.style.backgroundColor = "red";
        setTimeout(() => {timeBarRed.style.backgroundColor = "green";}, 500);
    }
    if (timer.getTimeValues().seconds === 10) {
        timeBarRed.style.backgroundColor = "red";
        setTimeout(() => {window.location.href = "http://127.0.0.1:5000/legendary_gamification/tortement";}, 500);
    }
});