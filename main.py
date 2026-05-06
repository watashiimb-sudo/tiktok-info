// Безопасное обновление элементов
function updateEl(id, text) {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
}

// ОСНОВНАЯ ФУНКЦИЯ ИНЪЕКЦИИ (ЗАЩИЩЕНА ОТ КРАШЕЙ)
async function processVideo() {
    const input = document.getElementById('vid-input');
    if (!input || !input.files.length) return alert("Файл не выбран!");
    
    const wrapper = document.getElementById('p-wrapper');
    const pBar = document.getElementById('p-bar');
    const consoleBox = document.getElementById('console');
    
    if (wrapper) wrapper.style.display = 'block';
    if (consoleBox) consoleBox.innerHTML = "> Подготовка памяти...";
    if (pBar) pBar.style.width = "10%";

    try {
        const file = input.files[0];
        const buffer = await file.arrayBuffer();
        const bytes = new Uint8Array(buffer);
        let count = 0;

        if (consoleBox) consoleBox.innerHTML += `<br>> Файл загружен: ${(file.size / (1024*1024)).toFixed(2)} MB`;

        // Используем setTimeout, чтобы разгрузить поток и не крашнуть вкладку
        await new Promise(resolve => setTimeout(resolve, 100));

        // Безопасный цикл: останавливаемся за 12 байт до конца
        const len = bytes.length - 12;
        for (let i = 0; i < len; i++) {
            // Ищем сигнатуру 'elst' (65 6c 73 74)
            if (bytes[i] === 0x65 && bytes[i+1] === 0x6C && bytes[i+2] === 0x73 && bytes[i+3] === 0x74) {
                count++;
                // Модификация байтов для обхода алгоритмов сжатия
                bytes[i + 8] = 0x10; 
                bytes[i + 9] = 0x00; 
                bytes[i + 10] = 0x00; 
                bytes[i + 11] = 0x01;
                
                // Чтобы не зависало на огромных файлах, делаем микро-паузу каждые 500 найденных блоков
                if (count % 500 === 0) await new Promise(r => setTimeout(r, 0));
            }
        }

        if (pBar) pBar.style.width = "100%";
        if (consoleBox) consoleBox.innerHTML += `<br>> Инъекция завершена! Найдено: ${count}`;

        if (count > 0) {
            const blob = new Blob([bytes], { type: "video/mp4" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "WATASHI_FIX_" + file.name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            if (consoleBox) consoleBox.innerHTML += `<br>> [SUCCESS] Файл отправлен на загрузку.`;
        } else {
            if (consoleBox) consoleBox.innerHTML += `<br>> [WARN] Метки 'elst' не найдены.`;
            alert("Этот тип MP4 не содержит нужных метаданных для патча.");
        }
    } catch (err) {
        console.error("CRASH PROTECT:", err);
        alert("Произошла критическая ошибка. Попробуйте файл поменьше или закройте лишние вкладки.");
        if (consoleBox) consoleBox.innerHTML += `<br>> [CRITICAL ERROR]`;
    }
}

// ФУНКЦИЯ АНАЛИЗА (С ИСПРАВЛЕННОЙ СТРАНОЙ)
async function analyzeVideo() {
    const linkInput = document.getElementById('tk-link');
    if (!linkInput || !linkInput.value) return;
    
    const fields = ['res-q', 'res-f', 'res-s', 'res-c'];
    fields.forEach(id => updateEl(id, "..."));

    try {
        const res = await fetch(`https://tiktok-info-production-c7c2.up.railway.app/get_info?link=${encodeURIComponent(linkInput.value)}`);
        const data = await res.json();
        
        if (data.status === "success") {
            updateEl('res-q', data.quality || "High");
            updateEl('res-f', data.fps || "60");
            updateEl('res-s', data.size || "-");
            
            // Проверка страны по всем возможным полям API
            const country = data.country || data.region || data.author_region || (curLang === 'ru' ? "Скрыто" : "Hidden");
            updateEl('res-c', country);
        } else {
            fields.forEach(id => updateEl(id, "Error"));
        }
    } catch (e) {
        fields.forEach(id => updateEl(id, "-"));
    }
}
