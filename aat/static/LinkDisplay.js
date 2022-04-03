const feedbackElems = document.querySelectorAll('.feedback-or-feedforward');
const urlExpression = /[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi;
var urlRegex = new RegExp(urlExpression);

for (let elem of feedbackElems) {
    const wordsArray = elem.innerHTML.split(' ');
    for (let i = 0; i < wordsArray.length; i++) {
        if (wordsArray[i].match(urlRegex)) {
            const url = wordsArray[i];
            wordsArray[i] = `<a href="${url}">${url}</a>`;
        }
    }
    elem.innerHTML = wordsArray.join(' ');
}