var timer = new easytimer.Timer();
const timeBar = document.querySelector(".time-bar")
const timeBarRed = document.getElementsByClassName("red-bar")[0]
const timeBarWhite = document.getElementsByClassName("white-bar")[0]

timer.start({precision: 'seconds', startValues: {seconds: 0}, target: {seconds: 10}})

timer.addEventListener('secondsUpdated', function(e) {
    timeBarRed.style.flex =  timer.getTimeValues().seconds * 0.2;
    timeBarRed.style.backgroundColor = "green";
    timeBarWhite.style.flex = (10 - timer.getTimeValues().seconds) * 0.2
    console.log(timer.getTotalTimeValues().seconds)
});