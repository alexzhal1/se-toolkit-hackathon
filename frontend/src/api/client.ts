const API_BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export interface User {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string;
}

export interface Material {
  id: number;
  user_id: number;
  title: string;
  content: string;
  explanation: string | null;
  created_at: string;
}

export interface Flashcard {
  id: number;
  material_id: number;
  front: string;
  back: string;
}

export interface ChatMessage {
  id: number;
  material_id: number;
  role: "user" | "assistant";
  content: string;
}

export const api = {
  auth(telegram_id: number, first_name: string): Promise<User> {
    return request("/auth", {
      method: "POST",
      body: JSON.stringify({ telegram_id, first_name }),
    });
  },

  getMaterials(userId: number): Promise<Material[]> {
    return request(`/materials?user_id=${userId}`);
  },

  getMaterial(id: number): Promise<Material> {
    return request(`/materials/${id}`);
  },

  createMaterial(userId: number, title: string, content: string): Promise<Material> {
    return request("/materials", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, title, content }),
    });
  },

  deleteMaterial(id: number): Promise<void> {
    return request(`/materials/${id}`, { method: "DELETE" });
  },

  explainMaterial(id: number): Promise<Material> {
    return request(`/materials/${id}/explain`, { method: "POST" });
  },

  getFlashcards(materialId: number): Promise<Flashcard[]> {
    return request(`/materials/${materialId}/flashcards`);
  },

  generateFlashcards(materialId: number): Promise<Flashcard[]> {
    return request(`/materials/${materialId}/flashcards`, { method: "POST" });
  },

  uploadFile(userId: number, title: string, file: File): Promise<Material> {
    const formData = new FormData();
    formData.append("user_id", String(userId));
    formData.append("title", title);
    formData.append("file", file);
    return fetch(`${API_BASE}/materials/upload`, {
      method: "POST",
      body: formData,
    }).then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Upload failed");
      }
      return res.json();
    });
  },

  getChatHistory(materialId: number): Promise<ChatMessage[]> {
    return request(`/materials/${materialId}/chat`);
  },

  sendChatMessage(materialId: number, message: string): Promise<ChatMessage> {
    return request(`/materials/${materialId}/chat`, {
      method: "POST",
      body: JSON.stringify({ message }),
    });
  },

  clearChat(materialId: number): Promise<void> {
    return request(`/materials/${materialId}/chat`, { method: "DELETE" });
  },
};
