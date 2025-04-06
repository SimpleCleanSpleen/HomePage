<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lazy's Homepage</title>
    <style>

/* Reset default margin and padding */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

img {
    width: 300 px;
}

body {
    font-family: Arial, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f0f0f0;
}

/* Button container with 2 rows and 5 columns */
.button-container {
    display: grid;
    grid-template-columns: repeat(5, 1fr); /* 5 equal columns */
    grid-gap: 20px; /* Space between buttons */
    width: 90%;
    height:30%;
    margin: 0 auto;
    padding:auto;
    text-align:center;
}

/* Style for the buttons */
.button {
    display: block;
    padding: 20px;
    text-align: center;
    background-color: #4CAF50;
    color: white;
    text-decoration: none;
    font-size: 30px;
    border-radius: 8px;
    box-shadow: 2 4px 6px rgba(0, 0, 0, 0.1);
    transition: background-color 0.3s ease, transform 0.3s ease;

}

.button:hover {
    background-color: #45a049;
    transform: translateY(-5px);
}

.button:active {
    transform: translateY(2px);

    </style>
</head>
<body>
    <div class="button-container">
        <a href="https://lemmy.ml/"
          class = "button">
          <img src="file:///run/user/1000/doc/975f4118/lemmy.png" alt="???">
          Lemmy
        </a>
        <a href="https://www.youtube.com/"
          class="button">
          Youtube
        </a>
        <a href="https://www.nerdwallet.com/" class="button">Nerd Walleton</a>
        <a href="https://cad.onshape.com/signin?_gl=1*vs94r2*_gcl_au*MTk4NDI2MTczMy4xNzQzODEwNzgx#_ga=2.37111208.982060149.1743810783-1833321486.1743810781" class="button">onShape</a>
        <a href="https://messages.google.com/web/u/0/conversations" class="button">Messages</a>
        <a href="https://drive.google.com/drive/home?dmr=1&ec=wgc-drive-globalnav-goto" class="button">Google Drive</a>
        <a href="https://notebooklm.google.com/?_gl=1*19983xu*_ga*OTAwMDUzODA1LjE3NDM4MTA5NzE.*_ga_W0LDH41ZCB*MTc0MzgxMDk3MS4xLjAuMTc0MzgxMDk3MS42MC4wLjA.&original_referer=https:%2F%2Fnotebooklm.google%23&pli=1" class="button">NoteBookLM</a>
        <a href="https://www.cheapshark.com/" class="button">Cheap Shark</a>
        <a href="https://calendar.google.com/calendar/u/0/r?pli=1" class="button">Google Calendar</a>
        <a href="https://mail.google.com/mail/u/0/#inbox" class="button">Gmail</a>
    </div>

</body>
</html>
