const express = require('express');
const ytDlp = require('yt-dlp-exec');
const path = require('path');

const app = express();
app.use(express.static(__dirname));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/get_info', async (req, res) => {
    const link = req.query.link;
    if (!link) return res.json({ status: 'error', message: 'Нет ссылки' });

    try {
        const info = await ytDlp(link, {
            dumpSingleJson: true,
            noWarnings: true,
        });

        const size = info.filesize || info.filesize_approx || 0;

        res.json({
            status: 'success',
            quality: `${info.width}x${info.height}`,
            fps: `${info.fps} FPS`,
            size: size ? `${(size / 1024 / 1024).toFixed(2)} MB` : 'Н/Д'
        });
    } catch (e) {
        res.json({ status: 'error', message: e.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Сервер запущен на порту ${PORT}`));
