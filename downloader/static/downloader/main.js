const supportedPlatforms = [
    "youtube.com",
    "youtu.be",
    "tiktok.com",
    "instagram.com",
    "facebook.com",
    "fb.watch",
    "x.com",
    "twitter.com"
  ];

  document.querySelector("form").addEventListener("submit", function (e) {
    const urlInput = this.querySelector("input[name='url']");
    const url = urlInput.value.trim();

    if (!supportedPlatforms.some(platform => url.includes(platform))) {
      e.preventDefault(); // Stop form submission
      alert("Please enter a valid video URL from YouTube, TikTok, Instagram, X, or Facebook.");
    }
  });


// const form = document.getElementById("download-form");
// const spinner = document.getElementById("spinner");
// const button = document.getElementById("download-btn");

//   form.addEventListener("htmx:beforeRequest", () => {
//     spinner.classList.remove("hidden");
//     button.disabled = true;
//     button.classList.add("opacity-50");
//   });

//   form.addEventListener("htmx:afterSwap", () => {
//     spinner.classList.add("hidden");
//     button.disabled = false;
//     button.classList.remove("opacity-50");
//   });

function showSpinner() {
  const spinner = document.getElementById("spinner");
  const button = document.getElementById("download-btn");

  spinner.classList.remove("hidden");
  button.disabled = true;
  button.classList.add("opacity-50");
}