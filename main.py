// --- ЗАМЕНИ ЭТИ ФУНКЦИИ В СВОЕМ <script> ---

// Вспомогательная функция для безопасного обновления текста
function updateEl(id, text) {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
}

async function processVideo() {
    const input = document.getElementById('vid-input');
    if (!input || !input.files.length) return alert("Файл не выбран!");
    
    const wrapper = document.getElementById('p-wrapper');
    const pBar = document.getElementById('p-bar');
    const consoleBox = document.getElementById('console');
    
    if (wrapper) wrapper.style.display = 'block';
    if (consoleBox) consoleBox.innerHTML = "> Инициализация...";
    if (pBar) pBar.style.width = "20%";

    try {
        const file = input.files[0];
        
        // Проверка на слишком большие файлы (защита от краша браузера)
        if (file.size > 500 * 1024 * 1024) {
            alert("Файл слишком большой (>500MB). Браузер может вылететь.");
        }

        const buffer = await file.arrayBuffer();
        const bytes = new Uint8Array(buffer);
        let count = 0;

        // ИСПРАВЛЕНО: i < bytes.length - 12, чтобы i + 11 всегда был внутри массива
        for (let i = 0; i < bytes.length - 12; i++) {
            if (bytes[i] === 0x65 && bytes[i+1] === 0x6C && bytes[i+2] === 0x73 && bytes[i+3] === 0x74) {
                count++;
                bytes[i + 8] = 0x10; 
                bytes[i + 9] = 0x00; 
                bytes[i + 10] = 0x00; 
                bytes[i + 11] = 0x01;
            }
        }

        if (pBar) pBar.style.width = "100%";
        if (consoleBox) consoleBox.innerHTML += `<br>> Найдено блоков: ${count}<br>> Готово!`;

        if (count > 0) {
            const blob = new Blob([bytes], { type: "video/mp4" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "WATASHI_FIX_" + file.name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } else {
            alert("Метаданные 'elst' не найдены. Видео уже обработано или имеет другой формат.");
        }
    } catch (err) {
        console.error(err);
        alert("Ошибка при обработке видео. Возможно, не хватает оперативной памяти.");
    }
}

async function analyzeVideo() {
    const linkInput = document.getElementById('tk-link');
    if (!linkInput || !linkInput.value) return alert(langData[curLang].errLink);
    
    const fields = ['res-q', 'res-f', 'res-s', 'res-c'];
    fields.forEach(id => updateEl(id, "..."));

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // Таймаут 10 секунд

        const res = await fetch(`https://tiktok-info-production-c7c2.up.railway.app/get_info?link=${encodeURIComponent(linkInput.value)}`, {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        const data = await res.json();
        
        if (data.status === "success") {
            updateEl('res-q', data.quality || "720p");
            updateEl('res-f', data.fps || "30");
            updateEl('res-s', data.size || "-");
            // Проверка всех возможных полей для страны
            const country = data.country || data.region || data.author_region || (curLang === 'ru' ? "Скрыто" : "Hidden");
            updateEl('res-c', country);
        } else {
            throw new Error("Invalid response");
        }
    } catch (e) {
        console.error(e);
        alert(curLang === 'ru' ? "Сервер не отвечает или ссылка неверна" : "Server error or invalid link");
        fields.forEach(id => updateEl(id, "-"));
    }
}
