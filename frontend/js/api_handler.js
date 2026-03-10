const API = {
    BASE_URL: '/api',

    async upload(file) {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch(`${this.BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        return await res.json();
    },

    async detect(sessionId, pageIndex) {
        const res = await fetch(`${this.BASE_URL}/detect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, page_index: pageIndex })
        });
        return await res.json();
    },

    async redact(sessionId, allMasks) {
        const res = await fetch(`${this.BASE_URL}/redact`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, masks: allMasks })
        });
        return await res.json();
    }
};
