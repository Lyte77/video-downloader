
let slowNetworkTimer;

// --- 1. SLOW NETWORK FEEDBACK LOGIC ---

// Fired BEFORE the HTMX request is sent. This is the perfect place to start the timer.
document.body.addEventListener('htmx:beforeRequest', function(evt) {
    const msg = document.getElementById("slow-network-msg");
    
    // Hide it initially (in case the previous attempt was slow)
    if(msg) msg.classList.add("hidden");

    // Start a timer for 8 seconds (8000 milliseconds). Adjust this duration as needed.
    slowNetworkTimer = setTimeout(() => {
        if(msg) {
            msg.classList.remove("hidden"); // Show the message
            console.log("Slow network detected - showing user feedback.");
        }
    }, 8000); 
});


document.body.addEventListener('htmx:afterOnLoad', function(evt) {
    
    clearTimeout(slowNetworkTimer);
    
    const msg = document.getElementById("slow-network-msg");
    if(msg) msg.classList.add("hidden"); // Hide the message once the process is complete
});




document.body.addEventListener("start-download", function(evt) {
    const data = evt.detail;
    
    console.log("Download Triggered for:", data);

    if (data.videoUrl) {
        window.location.href = data.videoUrl;
    }
    
    
    if (data.audioUrl) {
        setTimeout(() => {
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = data.audioUrl;
            document.body.appendChild(iframe);
            
            // Cleanup iframe after a minute
            setTimeout(() => iframe.remove(), 60000); 
        }, data.videoUrl ? 1000 : 0); // Only delay if we also downloaded a video
    }

    const btn = document.getElementById("download-btn");
    const spinner = document.getElementById("spinnerx");
    const btnText = btn ? btn.querySelector("span.truncate") : null;

    if (btn) {
        btn.disabled = false;
        btn.classList.remove("opacity-60", "cursor-not-allowed");
        if (btnText) btnText.textContent = "Download"; 
    }

    if (spinner) {
        spinner.classList.add("hidden");
    }
});


document.body.addEventListener('htmx:responseError', function (evt) {
    clearTimeout(slowNetworkTimer); // Ensure timer stops on error as well!
    
    const container = document.getElementById("transcript-container");
    container.innerHTML = `<div class="p-4 bg-red-100 text-red-700 rounded">Server Error: ${evt.detail.xhr.statusText}</div>`;
    
    // Also reset button on error!
    const btn = document.getElementById("download-btn");
    const spinner = document.getElementById("spinnerx");
    if (btn) {
        btn.disabled = false;
        btn.classList.remove("opacity-60", "cursor-not-allowed");
    }
    if (spinner) spinner.classList.add("hidden");
});