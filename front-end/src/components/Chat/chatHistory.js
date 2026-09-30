const CHAT_HISTORY_PREFIX = "medisafe_chat_history:";

export function getChatHistoryKey(user) {
  const identity = user?.email || user?.username;
  return identity
    ? `${CHAT_HISTORY_PREFIX}${encodeURIComponent(identity.toLowerCase())}`
    : null;
}

export function loadChatHistory(key) {
  if (!key) return [];

  try {
    const history = JSON.parse(sessionStorage.getItem(key) || "[]");
    return Array.isArray(history) ? history : [];
  } catch {
    try {
      sessionStorage.removeItem(key);
    } catch {}
    return [];
  }
}

export function saveChatHistory(key, messages) {
  if (!key) return;

  try {
    sessionStorage.setItem(key, JSON.stringify(messages));
  } catch {}
}

export function clearChatHistory(user) {
  const key = getChatHistoryKey(user);

  try {
    if (key) {
      sessionStorage.removeItem(key);
      return;
    }

    for (let index = sessionStorage.length - 1; index >= 0; index -= 1) {
      const storedKey = sessionStorage.key(index);
      if (storedKey?.startsWith(CHAT_HISTORY_PREFIX)) {
        sessionStorage.removeItem(storedKey);
      }
    }
  } catch {}
}