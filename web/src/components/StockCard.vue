<script setup lang="ts">
import { computed } from "vue";
import type { Stock } from "../types";

const props = defineProps<{ stock: Stock }>();

const priceDirection = computed<"up" | "down" | "flat">(() => {
  const c = props.stock.change;
  if (c === null) return "flat";
  return c > 0 ? "up" : c < 0 ? "down" : "flat";
});

const auctionLabel = computed(() => {
  const m = props.stock.auction_minutes;
  return m ? `${m}分盤` : null;
});

const bucketLabel = computed(() => {
  if (props.stock.bucket === "risk") return "即將進入處置";
  if (props.stock.bucket === "exiting") return "即將出關";
  return props.stock.measure ?? "處置中";
});

const periodLabel = computed(() => {
  const a = props.stock.period_start;
  const b = props.stock.period_end;
  if (!a || !b) return null;
  return `處置期間 ${a.slice(5).replace("-", "/")} - ${b.slice(5).replace("-", "/")}`;
});

const fmtPct = (v: number | null) =>
  v === null ? "—" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`;

const fmtNum = (v: number | null, digits = 2) =>
  v === null ? "—" : v.toFixed(digits);
</script>

<template>
  <article :class="['card', `card--${priceDirection}`]">
    <header class="card__head">
      <span class="card__name">{{ stock.name }}</span>
      <span class="card__code">{{ stock.code }}</span>
      <span v-if="stock.industry" class="tag tag--industry">{{ stock.industry }}</span>
    </header>

    <div class="card__price">
      <span class="card__close">{{ fmtNum(stock.close) }}</span>
      <span v-if="stock.change !== null" class="card__chg">
        {{ stock.change >= 0 ? "▲" : "▼" }} {{ Math.abs(stock.change).toFixed(2) }}
        ({{ fmtPct(stock.change_pct) }})
      </span>
    </div>

    <div class="card__row">
      <span class="card__bucket">{{ bucketLabel }}</span>
      <span v-if="auctionLabel" class="tag tag--auction">{{ auctionLabel }}</span>
    </div>

    <div class="card__tags">
      <span v-if="stock.notice_count_30d" class="tag tag--count">注意 {{ stock.notice_count_30d }}</span>
      <span v-if="stock.prepay_full" class="tag tag--prepay">預收</span>
      <span v-if="stock.can_intraday" class="tag tag--intraday">沖</span>
    </div>

    <footer v-if="stock.value_100m !== null || periodLabel" class="card__foot">
      <span v-if="stock.value_100m !== null">成交值 {{ fmtNum(stock.value_100m, 1) }}億</span>
      <span v-if="periodLabel">{{ periodLabel }}</span>
    </footer>
  </article>
</template>
