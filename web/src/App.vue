<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useSnapshotStore } from "./stores/snapshot";
import TabBar from "./components/TabBar.vue";
import StockCard from "./components/StockCard.vue";

const store = useSnapshotStore();
onMounted(store.load);

const stocks = computed(() => {
  if (!store.data) return [];
  return store.data[store.activeBucket];
});

const updatedAt = computed(() => {
  if (!store.data) return "";
  return new Date(store.data.updated_at).toLocaleString("zh-TW", {
    hour: "2-digit",
    minute: "2-digit",
    month: "2-digit",
    day: "2-digit",
  });
});
</script>

<template>
  <div class="app">
    <header class="app__header">
      <h1>處置股看板</h1>
      <span v-if="updatedAt" class="app__updated">更新於 {{ updatedAt }}</span>
    </header>

    <TabBar />

    <main class="app__main">
      <p v-if="store.loading" class="app__status">載入中…</p>
      <p v-else-if="store.error" class="app__status app__status--error">
        載入失敗：{{ store.error }}
      </p>
      <p v-else-if="stocks.length === 0" class="app__status">這個分類目前沒有股票</p>
      <div v-else class="app__grid">
        <StockCard v-for="s in stocks" :key="s.code" :stock="s" />
      </div>
    </main>
  </div>
</template>
