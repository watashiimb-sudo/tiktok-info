async function analyzeVideo() {
    const link = document.getElementById('tk-link').value;
    if(!link) return alert(curLang === 'ru' ? "Вставьте ссылку!" : "Paste link!");
    
    // Сброс и анимация загрузки
    const fields = ['res-q', 'res-f', 'res-s', 'res-c'];
    fields.forEach(id => document.getElementById(id).innerText = "...");

    try {
        const res = await fetch(`https://tiktok-info-production-c7c2.up.railway.app/get_info?link=${encodeURIComponent(link)}`);
        const data = await res.json();
        
        if(data.status === "success") {
            // Заполнение данных с проверкой на пустоту
            document.getElementById('res-q').innerText = data.quality || "720p";
            document.getElementById('res-f').innerText = data.fps || "30";
            document.getElementById('res-s').innerText = data.size || "MB";
            
            // ЛОГИКА ДЛЯ СТРАНЫ:
            // Ищем в country, если нет — в region, если нет — пишем "Скрыто"
            const region = data.country || data.region || data.author_location || (curLang === 'ru' ? "Скрыто" : "Hidden");
            document.getElementById('res-c').innerText = region;
            
        } else {
            alert(curLang === 'ru' ? "Ошибка: Данные не найдены" : "Error: Data not found");
            fields.forEach(id => document.getElementById(id).innerText = "-");
        }
    } catch(e) { 
        console.error("Ошибка API:", e);
        alert(curLang === 'ru' ? "Сервер недоступен" : "Server offline");
        fields.forEach(id => document.getElementById(id).innerText = "-");
    }
}
