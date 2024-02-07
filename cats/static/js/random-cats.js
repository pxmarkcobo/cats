const frame = document.body.querySelector('.frame')

let images = JSON.parse(document.getElementById('image-urls').textContent);
let imgCount = images.length;
const totalImages = images.length;
images.forEach(image => appendCard(image))

let current = frame.querySelector('.card:last-child')

document.querySelector('#like').onclick = () => {
  moveX = 1
  moveY = 0
  complete("likes")
}
document.querySelector('#hate').onclick = () => {
  moveX = -1
  moveY = 0
  complete("hates")
}

function appendCard(image) {
  const firstCard = frame.children[0]
  const newCard = document.createElement('div')
  newCard.className = 'card justify-content-end'
  newCard.style.backgroundImage = `url(${image})`
  if (firstCard) {
    frame.insertBefore(newCard, firstCard)
  }
  else {
    frame.appendChild(newCard)
  }
  imgCount++
}

function setTransform(x, y, deg, duration) {
  current.style.transform = `translate3d(${x}px, ${y}px, 0) rotate(${deg}deg)`
  if (duration) current.style.transition = `transform ${duration}ms`
}

function complete(action) {
    const style = window.getComputedStyle(current);
    const backgroundImage = style.backgroundImage;
    const regex = /url\(["']?(.*?)["']?\)/i;
    const matches = backgroundImage.match(regex);

    if (matches) {
        const imageUrl = matches[1];
        const actionArray = JSON.parse(localStorage.getItem(action) || "[]");

        if (!actionArray.includes(imageUrl)) {
            actionArray.push(imageUrl);
            localStorage.setItem(action, JSON.stringify(actionArray));
        }
    }
    const flyX = (Math.abs(moveX) / moveX) * innerWidth * 1.3
    const flyY = (moveY / moveX) * flyX
    setTransform(flyX, flyY, flyX / innerWidth * 50, innerWidth)

    const prev = current
    current = current.previousElementSibling
    appendCard(images[imgCount % totalImages ])
    setTimeout(() => frame.removeChild(prev), innerWidth)
}

function cancel() {
  setTransform(0, 0, 0, 100)
  setTimeout(() => current.style.transition = '', 100)
}
