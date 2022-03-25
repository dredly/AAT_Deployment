var timer = new easytimer.Timer();
const timeBar = document.querySelector(".time-bar")
const timeBarRed = document.getElementsByClassName("red-bar")[0]
const timeBarWhite = document.getElementsByClassName("white-bar")[0]
const timeShow = document.getElementsByClassName("timer")[0]

timer.start({countdown: true, startValues: {seconds: 10}});

timer.addEventListener('secondsUpdated', function(e) {
    timeShow.innerHTML = timer.getTimeValues().seconds.toString();
    timeBarWhite.style.flex =  timer.getTimeValues().seconds * 0.2;
    timeBarRed.style.flex = (10 - timer.getTimeValues().seconds) * 0.2
    console.log(timer.getTotalTimeValues().seconds)
    if (timer.getTimeValues().seconds <= 3 && timer.getTimeValues().seconds > 0) {
        timeBarRed.style.backgroundColor = "red";
        setTimeout(() => {timeBarRed.style.backgroundColor = "orange";}, 500);
        timeShow.style.color = "red";
        setTimeout(() => {timeShow.style.color = "orange";}, 500);
    }
    if (timer.getTimeValues().seconds === 0) {
        timeBarRed.style.backgroundColor = "red";
        timeShow.style.color = "red";
        setTimeout(() => {window.location.href = "http://127.0.0.1:5000/legendary_gamification/tortement";}, 500);
    }
});