import { useCallback, useEffect, useState } from "react";
import { api } from "../services/api.js";

// Loads categories and menu items from the backend.
export function useMenu() {
  const [data, setData] = useState({ categories: [], items: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const reload = useCallback(async () => {
    try {
      const [categories, items] = await Promise.all([api.categories(), api.menu()]);
      setData({ categories, items });
      setError("");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { reload(); }, [reload]);
  return { ...data, loading, error, reload };
}
