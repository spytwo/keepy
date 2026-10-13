
const form = document.querySelector("#entry-form");
const contentInput = document.querySelector("#content");
const submitButton = document.querySelector("#submit-button");
const entriesContainer = document.querySelector("#entries");
const entryCount = document.querySelector("#entry-count");
const statusMessage = document.querySelector("#status");

async function request(url, options = {}) {
    const response = await fetch(url, options);

    if (!response.ok) {
        let message = `Ошибка HTTP ${response.status}`;

        try {
            const data = await response.json();
            message = data.detail ?? message;
        } catch {
            // Ответ сервера не обязательно содержит JSON.
        }

        throw new Error(
            typeof message === "string" ? message : JSON.stringify(message)
        );
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

function renderContent(element, content) {
    const urlPattern = /https?:\/\/[^\s<>"']+/g;
    let lastIndex = 0;

    for (const match of content.matchAll(urlPattern)) {
        const url = match[0];
        const start = match.index;

        // Отделяем знаки пунктуации в конце ссылки.
        const trimmedUrl = url.replace(/[.,!?;:)]+$/, "");
        const trailing = url.slice(trimmedUrl.length);

        element.append(
            document.createTextNode(content.slice(lastIndex, start))
        );

        if (trimmedUrl) {
            const link = document.createElement("a");
            link.href = trimmedUrl;
            link.textContent = trimmedUrl;
            link.target = "_blank";
            link.rel = "noopener noreferrer";

            element.append(link);
        }

        element.append(document.createTextNode(trailing));
        lastIndex = start + url.length;
    }

    element.append(document.createTextNode(content.slice(lastIndex)));
}

function renderEntries(entries) {
    entriesContainer.replaceChildren();
    entryCount.textContent = entries.length;

    if (entries.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "Здесь пока пусто. Сохрани что-нибудь интересное.";
        entriesContainer.append(empty);
        return;
    }

    for (const entry of entries) {
        const item = document.createElement("article");
        item.className = "entry";

        const text = document.createElement("p");
        text.className = "entry-content";
        renderContent(text, entry.content);

        const deleteButton = document.createElement("button");
        deleteButton.className = "delete-button";
        deleteButton.type = "button";
        deleteButton.textContent = "Удалить";
        deleteButton.setAttribute("aria-label", "Удалить запись");

        deleteButton.addEventListener("click", async () => {
            if (!confirm("Удалить эту запись?")) {
                return;
            }

            deleteButton.disabled = true;

            try {
                await request(`/entries/${entry.id}`, {
                    method: "DELETE",
                });

                await loadEntries();
                statusMessage.textContent = "";
            } catch (error) {
                statusMessage.textContent =
                    `Не удалось удалить запись: ${error.message}`;
                deleteButton.disabled = false;
            }
        });

        item.append(text, deleteButton);
        entriesContainer.append(item);
    }
}

async function loadEntries() {
    const entries = await request("/entries");
    renderEntries(entries);
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const content = contentInput.value.trim();

    if (!content) {
        statusMessage.textContent = "Введи текст записи.";
        return;
    }

    submitButton.disabled = true;
    statusMessage.textContent = "";

    try {
        await request("/entries", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ content }),
        });

        contentInput.value = "";
        await loadEntries();
    } catch (error) {
        statusMessage.textContent =
            `Не удалось добавить запись: ${error.message}`;
    } finally {
        submitButton.disabled = false;
        contentInput.focus();
    }
});

loadEntries().catch((error) => {
    statusMessage.textContent =
        `Не удалось загрузить записи: ${error.message}`;
});
