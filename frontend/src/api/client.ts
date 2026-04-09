const API_BASE = "/api";

export interface User {
  id: number;
  email: string;
  login: string;
  created_at: string;
}

export interface AuthResponse {
  user: User;
  token: string;
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

export interface QuizQuestion {
  id: number;
  question_text: string;
  options: string[];
  correct_answer_indices: number[];
  is_multi: boolean;
  explanation: string;
}

export interface Quiz {
  id: number;
  material_id: number;
  title: string;
  created_at: string;
  questions: QuizQuestion[];
}

function getToken(): string | null {
  return localStorage.getItem("studybot_token");
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    headers,
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  register(email: string, login: string, password: string): Promise<AuthResponse> {
    return request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, login, password }),
    });
  },

  login(login: string, password: string): Promise<AuthResponse> {
    return request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ login, password }),
    });
  },

  getMaterials(): Promise<Material[]> {
    return request("/materials");
  },

  getMaterial(id: number): Promise<Material> {
    return request(`/materials/${id}`);
  },

  createMaterial(title: string, content: string): Promise<Material> {
    return request("/materials", {
      method: "POST",
      body: JSON.stringify({ title, content }),
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

  uploadFile(title: string, file: File): Promise<Material> {
    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);
    const token = getToken();
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return fetch(`${API_BASE}/materials/upload`, {
      method: "POST",
      headers,
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

  getQuiz(materialId: number): Promise<Quiz | null> {
    return request(`/materials/${materialId}/quiz`);
  },

  generateQuiz(materialId: number): Promise<Quiz> {
    return request(`/materials/${materialId}/quiz`, { method: "POST" });
  },

  submitQuiz(
    quizId: number,
    answers: Record<number, number[]>
  ): Promise<{ score: number; total: number; attempt_id: number }> {
    return request(`/quizzes/${quizId}/submit`, {
      method: "POST",
      body: JSON.stringify({ answers }),
    });
  },

  getReviewQueue(): Promise<ReviewFlashcard[]> {
    return request("/flashcards/review");
  },

  reviewFlashcard(cardId: number, quality: number): Promise<Flashcard> {
    return request(`/flashcards/${cardId}/review`, {
      method: "POST",
      body: JSON.stringify({ quality }),
    });
  },

  getStats(): Promise<UserStats> {
    return request("/users/me/stats");
  },
};

export interface ReviewFlashcard extends Flashcard {
  material_title: string;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
}

export interface QuizAttemptSummary {
  quiz_id: number;
  score: number;
  total: number;
  completed_at: string;
}

export interface UserStats {
  materials_count: number;
  flashcards_count: number;
  flashcards_due: number;
  flashcards_learned: number;
  quiz_attempts: number;
  quiz_avg_pct: number;
  recent_attempts: QuizAttemptSummary[];
}
