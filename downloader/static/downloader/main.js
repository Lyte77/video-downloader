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