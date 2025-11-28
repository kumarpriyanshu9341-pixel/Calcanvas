function startListening() {
    const micAnimation = document.getElementById("micAnimation");
    const speakerAnimation = document.getElementById("speakerAnimation");
    const loader = document.getElementById("loader");
    const clickSound = document.getElementById("clickSound");

    // Play click sound
    clickSound.play();

    // Show mic animation and loader
    micAnimation.style.display = "block";
    speakerAnimation.style.display = "none";
    loader.style.display = "block";

    fetch('/start-voice-assistant')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            micAnimation.style.display = "none";
            speakerAnimation.style.display = "block";
            loader.style.display = "none";
        })
        .catch(error => {
            console.error('Error:', error);
            micAnimation.style.display = "none";
            loader.style.display = "none";
        });
}

// Theme Toggle
document.getElementById('themeButton').addEventListener('click', () => {
    document.body.classList.toggle('light-theme');
});
