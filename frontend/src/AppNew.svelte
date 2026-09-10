<script lang="ts">
  import { onMount } from "svelte";

  type Ayah = { number: number; text: string; surah?: { number: number; name: string }; numberInSurah?: number };
  type SearchMatch = { number: number; text: string; surah: { number: number; name: string }; numberInSurah: number };
  type Surah = { number: number; name: string; englishName: string; numberOfAyahs: number; revelationType: string };
  type SurahData = { number: number; name: string; englishName: string; numberOfAyahs: number; revelationType: string; ayahs: Ayah[] };
  type ReadingHistory = { reference: string; title: string; timestamp: number };
  type Hadith = { text: string; topic: string; source: string };

  let reference = $state("1:1");
  let query = $state("");
  let activeTab = $state("القرآن");
  let ayah = $state<Ayah | null>(null);
  let results = $state<SearchMatch[]>([]);
  let loading = $state(false);
  let message = $state("أدخل رقم الآية أو ابحث عن كلمة من القرآن الكريم");
  let backendStatus = $state("جاري الاتصال بالخادم");
  let assistantQuery = $state("");
  let surahs = $state<Surah[]>([]);
  let tafsirText = $state("");
  let translationText = $state("");
  let favorites = $state<string[]>([]);
  let readingHistory = $state<ReadingHistory[]>([]);
  let theme = $state<"light" | "dark">("light");
  let showSurahs = $state(false);
  let currentSurah = $state<SurahData | null>(null);
  let surahLoading = $state(false);
  let surahsLoading = $state(false);
  let currentPage = $state("home");
  let searchPage = $state(1);
  let fontScale = $state(1);
  let copyNotice = $state("");
  let tasbihCount = $state(0);
  let tasbihTarget = $state(33);
  let tasbihIndex = $state(0);
  let selectedDhikr = $state(0);
  let hadithTopic = $state("الكل");
  const dhikrItems = [
    { title: "أذكار الصباح", text: "أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له." },
    { title: "أذكار المساء", text: "أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له." },
    { title: "سيد الاستغفار", text: "اللهم أنت ربي لا إله إلا أنت، خلقتني وأنا عبدك، وأنا على عهدك ووعدك ما استطعت." },
    { title: "ذكر السكينة", text: "حسبي الله لا إله إلا هو، عليه توكلت وهو رب العرش العظيم." },
  ];
  const tasbihItems = [
    { title: "سبحان الله", text: "سُبْحَانَ اللهِ", target: 33 },
    { title: "الحمد لله", text: "الْحَمْدُ لِلَّهِ", target: 33 },
    { title: "الله أكبر", text: "اللهُ أَكْبَرُ", target: 33 },
    { title: "لا إله إلا الله", text: "لَا إِلَهَ إِلَّا اللهُ وَحْدَهُ لَا شَرِيكَ لَهُ", target: 1 },
  ];
  const hadithItems: Hadith[] = [
    { text: "إنما الأعمال بالنيات، وإنما لكل امرئ ما نوى.", topic: "النية", source: "متفق عليه" },
    { text: "من كان يؤمن بالله واليوم الآخر فليقل خيرًا أو ليصمت.", topic: "الأخلاق", source: "متفق عليه" },
    { text: "لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه.", topic: "الأخلاق", source: "متفق عليه" },
    { text: "المسلم من سلم المسلمون من لسانه ويده.", topic: "المعاملات", source: "متفق عليه" },
    { text: "من لا يَرحم لا يُرحم.", topic: "الرحمة", source: "متفق عليه" },
    { text: "خيركم من تعلم القرآن وعلمه.", topic: "القرآن", source: "رواه البخاري" },
    { text: "لا ضرر ولا ضرار.", topic: "المعاملات", source: "رواه ابن ماجه" },
    { text: "الطهور شطر الإيمان.", topic: "الطهارة", source: "رواه مسلم" },
    { text: "أحب الأعمال إلى الله أدومها وإن قل.", topic: "العبادة", source: "متفق عليه" },
    { text: "الكلمة الطيبة صدقة.", topic: "الأخلاق", source: "متفق عليه" },
    { text: "تبسمك في وجه أخيك لك صدقة.", topic: "المعاملات", source: "رواه الترمذي" },
    { text: "اتق الله حيثما كنت، وأتبع السيئة الحسنة تمحها، وخالق الناس بخلق حسن.", topic: "التقوى", source: "رواه الترمذي" },
    { text: "الراحمون يرحمهم الرحمن، ارحموا من في الأرض يرحمكم من في السماء.", topic: "الرحمة", source: "رواه الترمذي" },
    { text: "من سلك طريقًا يلتمس فيه علمًا، سهل الله له به طريقًا إلى الجنة.", topic: "العلم", source: "رواه مسلم" },
    { text: "الدعاء هو العبادة.", topic: "الدعاء", source: "رواه الترمذي" },
    { text: "لا تغضب.", topic: "تهذيب النفس", source: "رواه البخاري" },
    { text: "يسروا ولا تعسروا، وبشروا ولا تنفروا.", topic: "الدعوة", source: "متفق عليه" },
    { text: "إن الله كتب الإحسان على كل شيء.", topic: "الإحسان", source: "رواه مسلم" },
    { text: "المؤمن للمؤمن كالبنيان يشد بعضه بعضًا.", topic: "التكافل", source: "متفق عليه" },
    { text: "من غشنا فليس منا.", topic: "الأمانة", source: "رواه مسلم" },
  ];
  const hadithTopics = ["الكل", ...Array.from(new Set(hadithItems.map((item) => item.topic)))];
  let searchScope = $state("all");
  let siteSearchResults = $state<{ title: string; type: string; text: string; href: string }[]>([]);
  const searchPageSize = 6;
  const apiBase = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
  const apiUrl = (path: string) => `${apiBase}${path}`;

  async function readApiPayload(response: Response) {
    const responseText = await response.text();
    try {
      return JSON.parse(responseText);
    } catch {
      throw new Error(response.ok ? "تعذر قراءة استجابة الخادم" : "الخادم غير متاح حاليًا، حاول مرة أخرى بعد قليل");
    }
  }

  const visibleResults = $derived(results.slice(0, searchPage * searchPageSize));
  const visibleHadith = $derived(hadithTopic === "الكل" ? hadithItems : hadithItems.filter((item) => item.topic === hadithTopic));

  function normalizeArabic(value: string) {
    return value
      .trim()
      .toLowerCase()
      .replace(/^سورة\s+/, "")
      .replace(/[ًٌٍَُِّْـ]/g, "")
      .replace(/[إأآا]/g, "ا")
      .replace(/ة/g, "ه");
  }

  function findSurah(value: string) {
    const normalized = normalizeArabic(value);
    return surahs.find((surah) => normalizeArabic(surah.name) === normalized || surah.englishName.toLowerCase() === normalized);
  }

  function resolveReference(value: string) {
    const normalized = value.trim();
    if (/^\d{1,3}:\d{1,3}$/.test(normalized)) return normalized;
    const match = normalized.match(/^(.+?)[\s:،/-]+(\d{1,3})$/);
    if (!match) return null;
    const surah = findSurah(match[1]);
    return surah ? `${surah.number}:${match[2]}` : null;
  }

  async function loadAyah(value = reference) {
    const normalized = resolveReference(value);
    if (!normalized) {
      message = "اكتب اسم السورة ورقم الآية، مثل: البقرة 255 أو 2:255";
      return;
    }
    reference = normalized;
    loading = true;
    message = "جاري تحميل الآية...";
    try {
      const response = await fetch(apiUrl(`/api/quran?ayah=${encodeURIComponent(normalized)}`));
      const payload = await readApiPayload(response);
      if (!response.ok || payload.code !== 200) throw new Error(payload.error);
      ayah = payload.data;
      results = [];
      currentSurah = null;
      localStorage.setItem("quran-last-reading", normalized);
      readingHistory = [{ reference: normalized, title: ayah?.surah?.name || "القرآن الكريم", timestamp: Date.now() }, ...readingHistory.filter((item) => item.reference !== normalized)].slice(0, 8);
      localStorage.setItem("quran-reading-history", JSON.stringify(readingHistory));
      message = `سورة ${ayah?.surah?.name || "القرآن"} · الآية ${ayah?.numberInSurah || ""}`;
    } catch (error) {
      message = error instanceof Error ? error.message : "تعذر تحميل الآية";
    } finally {
      loading = false;
    }
  }

  async function searchQuran() {
    if (!query.trim()) return;
    const matchingSurah = findSurah(query);
    if (matchingSurah && searchScope === "quran") {
      window.location.href = `/quran?surah=${matchingSurah.number}`;
      return;
    }
    ayah = null;
    currentSurah = null;
    results = [];
    if (searchScope === "quran") siteSearchResults = [];
    if (searchScope !== "quran") {
      runSiteSearch(query);
      if (searchScope === "adhkar") return;
    }
    loading = true;
    message = "جاري البحث في القرآن الكريم...";
    try {
      const response = await fetch(apiUrl(`/api/quran?search=${encodeURIComponent(query.trim())}`));
      const payload = await readApiPayload(response);
      if (!response.ok || payload.code !== 200) throw new Error(payload.error);
      results = payload.data?.matches || [];
      searchPage = 1;
      ayah = null;
      message = `تم العثور على ${results.length} نتيجة`;
    } catch (error) {
      message = error instanceof Error ? error.message : "تعذر تنفيذ البحث";
    } finally {
      loading = false;
    }
  }

  function runSiteSearch(value: string) {
    const needle = value.trim().toLowerCase();
    const matches: { title: string; type: string; text: string; href: string }[] = [];
    if (searchScope !== "quran") {
      surahs.filter((item) => `${item.name} ${item.englishName}`.toLowerCase().includes(needle)).slice(0, 8).forEach((item) => matches.push({ title: `سورة ${item.name}`, type: "سورة", text: `${item.numberOfAyahs} آية · ${item.revelationType === "Meccan" ? "مكية" : "مدنية"}`, href: `/quran?surah=${item.number}` }));
      dhikrItems.filter((item) => `${item.title} ${item.text}`.toLowerCase().includes(needle)).forEach((item) => matches.push({ title: item.title, type: "ذكر", text: item.text, href: "/adhkar" }));
      if ("السبحة الإلكترونية التسبيح".includes(needle)) matches.push({ title: "السبحة الإلكترونية", type: "أداة", text: "أذكار التسبيح المتسلسلة", href: "/tasbih" });
    }
    siteSearchResults = matches;
    if (searchScope === "adhkar") results = [];
    message = `تم العثور على ${matches.length} نتيجة في الموقع`;
  }

  async function checkBackend() {
    const healthCacheKey = "rushd-health-status";
    const healthCacheTtl = 15_000;
    try {
      const cached = JSON.parse(localStorage.getItem(healthCacheKey) || "null");
      if (cached && Date.now() - cached.timestamp < healthCacheTtl) {
        backendStatus = cached.status;
        return;
      }
    } catch {
      localStorage.removeItem(healthCacheKey);
    }
    try {
      const response = await fetch(apiUrl("/.health"), { headers: { Accept: "application/json" } });
      const payload = await readApiPayload(response);
      backendStatus = response.ok && payload.status === "healthy" ? "الخادم متصل" : response.ok ? "الخادم متصل جزئيًا" : "الخادم غير مكتمل";
      localStorage.setItem(healthCacheKey, JSON.stringify({ status: backendStatus, timestamp: Date.now() }));
    } catch {
      backendStatus = "الخادم غير متصل";
      localStorage.setItem(healthCacheKey, JSON.stringify({ status: backendStatus, timestamp: Date.now() }));
    }
  }

  async function loadSurahs() {
    surahsLoading = true;
    try {
      const response = await fetch(apiUrl("/api/surahs"));
      const payload = await readApiPayload(response);
      if (response.ok && payload.code === 200) surahs = payload.data;
    } catch {
      message = "تعذر تحميل فهرس السور";
    } finally {
      surahsLoading = false;
    }
  }

  async function loadSurah(surah: Surah) {
    showSurahs = false;
    surahLoading = true;
    activeTab = "القرآن";
    message = `جاري فتح سورة ${surah.name}...`;
    try {
      const response = await fetch(apiUrl(`/api/quran?surah=${surah.number}`));
      const payload = await readApiPayload(response);
      if (!response.ok || payload.code !== 200) throw new Error(payload.error);
      currentSurah = payload.data;
      reference = `${surah.number}:1`;
      localStorage.setItem("quran-last-surah", String(surah.number));
      message = `سورة ${surah.name} · ${surah.numberOfAyahs} آية`;
    } catch (error) {
      message = error instanceof Error ? error.message : "تعذر فتح السورة";
    } finally {
      surahLoading = false;
    }
  }

  async function loadStudyData(kind: "tafsir" | "translation") {
    if (!reference.trim()) return;
    loading = true;
    try {
      const response = await fetch(apiUrl(`/api/${kind}?ayah=${encodeURIComponent(reference.trim())}`));
      const payload = await readApiPayload(response);
      if (!response.ok || payload.code !== 200) throw new Error(payload.error);
      if (kind === "tafsir") tafsirText = payload.data.text;
      else translationText = payload.data.text;
    } catch (error) {
      message = error instanceof Error ? error.message : "تعذر تحميل المصدر";
    } finally {
      loading = false;
    }
  }

  function toggleFavorite() {
    const key = reference.trim();
    favorites = favorites.includes(key) ? favorites.filter((item) => item !== key) : [...favorites, key];
    localStorage.setItem("quran-favorites", JSON.stringify(favorites));
  }

  function toggleTheme() {
    theme = theme === "light" ? "dark" : "light";
    localStorage.setItem("quran-theme", theme);
  }

  async function copyAyah(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      copyNotice = "تم نسخ الآية";
      window.setTimeout(() => copyNotice = "", 1800);
    } catch {
      copyNotice = "تعذر النسخ من المتصفح";
    }
  }

  async function copyHadith(item: Hadith) {
    await copyAyah(`${item.text}\n\n${item.source}`);
  }

  async function shareAyah(text: string, ayahReference = reference) {
    const shareUrl = `${window.location.origin}/quran?ayah=${encodeURIComponent(ayahReference)}`;
    try {
      if (navigator.share) {
        await navigator.share({ title: `آية ${ayahReference}`, text, url: shareUrl });
      } else {
        await navigator.clipboard.writeText(`${text}\n\n${shareUrl}`);
        copyNotice = "تم نسخ الآية والرابط";
        window.setTimeout(() => copyNotice = "", 1800);
      }
    } catch {
      // Sharing can be cancelled by the user; no error state is needed.
    }
  }

  function adjustFont(delta: number) {
    fontScale = Math.min(1.3, Math.max(0.85, Number((fontScale + delta).toFixed(2))));
  }

  function incrementTasbih() {
    const target = tasbihItems[tasbihIndex].target;
    if (tasbihCount + 1 >= target) {
      tasbihCount = 0;
      tasbihIndex = (tasbihIndex + 1) % tasbihItems.length;
      tasbihTarget = tasbihItems[tasbihIndex].target;
      copyNotice = `اكتمل الذكر، انتقلنا إلى ${tasbihItems[tasbihIndex].title}`;
      window.setTimeout(() => copyNotice = "", 2200);
    } else {
      tasbihCount += 1;
    }
    localStorage.setItem("quran-tasbih-count", String(tasbihCount));
    localStorage.setItem("quran-tasbih-index", String(tasbihIndex));
  }

  function resetTasbih() {
    tasbihCount = 0;
    tasbihIndex = 0;
    tasbihTarget = tasbihItems[0].target;
    localStorage.setItem("quran-tasbih-count", "0");
    localStorage.setItem("quran-tasbih-index", "0");
  }

  function openSurah(surah: Surah) {
    loadSurah(surah);
  }

  function navigateSurah(offset: number) {
    if (!currentSurah) return;
    const next = surahs.find((item) => item.number === currentSurah?.number + offset);
    if (next) loadSurah(next);
  }

  function chooseResult(item: SearchMatch) {
    reference = `${item.surah.number}:${item.numberInSurah}`;
    loadAyah(reference);
  }

  function askAssistant() {
    query = assistantQuery;
    activeTab = "القرآن";
    searchQuran();
  }

  function showMoreResults() {
    searchPage += 1;
  }

  function pageTitle() {
    const titles: Record<string, string> = { quran: "المصحف والقراءة", search: "ابحث في القرآن", tafsir: "تفسير الآيات", hadith: "مكتبة الأحاديث", adhkar: "أذكار المسلم", tasbih: "السبحة الإلكترونية", mushaf: "المصحف والقراءة", translations: "ترجمات القرآن", favorites: "محفوظاتي" };
    return titles[currentPage] || "اقرأ، ابحث، وتدبّر";
  }

  function pageDescription() {
    const descriptions: Record<string, string> = { quran: "تصفح السور من القائمة الجانبية واقرأ النص بتركيز ووضوح.", search: "ابحث باسم السورة أو بكلمة من الآية، ثم افتح النتيجة مباشرة.", tafsir: "اقرأ المعنى الميسر للآية مع الاحتفاظ بالنص والمصدر أمامك.", hadith: "مختارات حديثية قصيرة مصنفة لتقرأها وتنسخها بسهولة.", adhkar: "أذكار يومية مرتبة لتقرأها بهدوء وتحفظها في روتينك.", tasbih: "سبحة إلكترونية بسيطة تحفظ العدد على جهازك وتساعدك على الاستمرار.", mushaf: "قارئ القرآن للنص والآيات والتفسير والترجمات من مكان واحد.", translations: "قارن ترجمة الآية مع النص العربي من داخل قارئ القرآن.", favorites: "آياتك المحفوظة في مكان واحد، لتعود إليها وقتما تشاء." };
    return descriptions[currentPage] || "وصول هادئ وموثوق إلى آيات القرآن الكريم، مع بحث سريع ومصادر قابلة للتوسع.";
  }

  function isReaderPage() {
    return currentPage === "quran" || currentPage === "mushaf";
  }

  function isKnownPage() {
    return ["home", "mushaf", "quran", "search", "tafsir", "hadith", "adhkar", "tasbih", "translations", "favorites"].includes(currentPage);
  }

  function isNotFoundPage() {
    return !isKnownPage();
  }

  onMount(() => {
    currentPage = window.location.pathname.replace("/", "") || "home";
    const urlParams = new URLSearchParams(window.location.search);
    const requestedAyah = urlParams.get("ayah");
    const requestedSurah = Number(urlParams.get("surah"));
    activeTab = currentPage === "tafsir" ? "التفسير" : currentPage === "hadith" ? "الأحاديث" : "القرآن";
    theme = (localStorage.getItem("quran-theme") as "light" | "dark") || "light";
    tasbihCount = Number(localStorage.getItem("quran-tasbih-count") || "0");
    tasbihIndex = Number(localStorage.getItem("quran-tasbih-index") || "0") % tasbihItems.length;
    tasbihTarget = tasbihItems[tasbihIndex].target;
    try {
      favorites = JSON.parse(localStorage.getItem("quran-favorites") || "[]");
    } catch {
      favorites = [];
    }
    try {
      readingHistory = JSON.parse(localStorage.getItem("quran-reading-history") || "[]");
    } catch {
      readingHistory = [];
    }
    reference = localStorage.getItem("quran-last-reading") || reference;
    checkBackend();
    loadSurahs().then(() => {
      if (isReaderPage() && requestedSurah) {
        const requested = surahs.find((item) => item.number === requestedSurah);
        if (requested) loadSurah(requested);
      }
    });
    if (requestedAyah) {
      reference = requestedAyah;
      loadAyah(requestedAyah);
    } else if (!["quran", "mushaf", "search", "hadith", "favorites"].includes(currentPage)) {
      loadAyah();
    }
    if (currentPage === "tafsir") loadStudyData("tafsir");
    if (currentPage === "translations") loadStudyData("translation");
  });
</script>

<div class:dark-mode={theme === "dark"} class="quran-app" dir="rtl">
  <header class="app-header">
    <a class="brand-wrap" href="/"><span class="brand-mark"><img src="/icon.png" alt="" /></span><span class="brand-copy"><strong>Rushd — رُشد</strong><small>رفيقك في تدبر القرآن</small></span></a>
    <nav class="app-nav"><a class:active={currentPage === "home"} href="/">الرئيسية</a><a class:active={isReaderPage()} href="/mushaf">المصحف</a><a class:active={currentPage === "search"} href="/search">البحث</a><a class:active={currentPage === "favorites"} href="/favorites">المحفوظات</a><a href="/#about">نبذة</a><a href="/#contact">تواصل</a></nav>
    <div class="header-tools"><span class="connection-state">● {backendStatus}</span><button class="theme-button" type="button" onclick={toggleTheme}>{theme === "light" ? "☾" : "☀"}</button></div>
  </header>

  {#if showSurahs}
    <div class="drawer-backdrop" role="presentation" onclick={() => showSurahs = false}></div>
    <aside class="surah-drawer"><div class="drawer-head"><h2>فهرس السور</h2><button type="button" onclick={() => showSurahs = false}>إغلاق</button></div><div class="surah-grid">{#each surahs as surah}<button type="button" onclick={() => openSurah(surah)}><strong>{surah.number}. {surah.name}</strong><small>{surah.englishName} · {surah.numberOfAyahs} آية</small></button>{/each}</div></aside>
  {/if}

  <main class="reader-layout">
    <section class="reader-hero" class:compact-hero={currentPage !== "home"}>
      <div class="hero-kicker">بِسْمِ اللهِ الرَّحْمَنِ الرَّحِيمِ</div>
      <h1>{pageTitle()}</h1>
      <p>{pageDescription()}</p>
      {#if ["quran", "mushaf", "search"].includes(currentPage)}
        <div class="reader-actions">
          <form class="reference-form" onsubmit={(event) => { event.preventDefault(); loadAyah(); }}><label for="reference">افتح آية بالمرجع</label><div class="input-row"><input id="reference" bind:value={reference} placeholder="البقرة 255 أو 2:255" /><button type="submit">فتح الآية</button></div><small class="field-hint">اكتب اسم السورة ورقم الآية أو المرجع الرقمي.</small></form>
          <form class="search-form" onsubmit={(event) => { event.preventDefault(); searchQuran(); }}><label for="search">ابحث في القرآن والسور</label><div class="input-row"><input id="search" bind:value={query} placeholder="اسم سورة أو كلمة من آية" /><button type="submit">بحث</button></div><small class="field-hint">جرّب: البقرة، الصبر، الرحمة.</small></form>
        </div>
      {/if}
    </section>

    {#if isNotFoundPage()}
      <section class="special-page not-found-page"><span class="section-label">404 · الصفحة غير موجودة</span><h2>لم نعثر على هذه الصفحة</h2><p>قد يكون الرابط غير صحيح أو أن الصفحة انتقلت إلى مكان آخر.</p><div class="not-found-actions"><a class="primary-action" href="/">العودة للرئيسية</a><a class="outline-button" href="/mushaf">فتح المصحف</a></div></section>
    {/if}

    {#if currentPage === "home"}
      <section class="landing-intro" id="about"><div class="landing-intro-copy"><span class="section-label">عن Rushd — رُشد</span><h2>مساحة هادئة للقراءة والفهم والتدبر</h2><p>Rushd منصة قرآنية تساعدك على الوصول إلى الآيات، التفاسير، والترجمات من مصادر واضحة، مع تجربة قراءة بسيطة ومريحة.</p><a class="primary-action" href="/mushaf">ابدأ القراءة <span>←</span></a></div><div class="landing-intro-mark" aria-hidden="true"><img src="/icon.png" alt="" /><small>اقرأ · افهم · تدبّر</small></div></section>
      <section class="landing-guide"><div class="section-heading-row"><div><span class="section-label">دليل الاستخدام</span><h2>كل ما تحتاجه في ثلاث خطوات</h2></div><a class="text-link" href="/mushaf">فتح المصحف ←</a></div><div class="guide-grid"><article><span>01</span><h3>اختر السورة</h3><p>افتح المصحف واستخدم فهرس السور الجانبي للوصول إلى السورة التي تريدها.</p></article><article><span>02</span><h3>اقرأ الآية</h3><p>تنقل بين الآيات، احفظ موضعك، وانسخ أو شارك الآية مع مصدرها.</p></article><article><span>03</span><h3>تدبّر المعنى</h3><p>افتح تبويبات التفسير والترجمة، أو ابحث عن موضوع أو اسم سورة.</p></article></div></section>
      {#if readingHistory.length}<section class="continue-strip"><div><span class="section-label">متابعة القراءة</span><h2>آخر ما قرأت: سورة {readingHistory[0].title}</h2><p>الآية {readingHistory[0].reference} · يمكنك العودة إلى موضعك مباشرة.</p></div><a class="outline-button" href={`/mushaf?ayah=${readingHistory[0].reference}`}>متابعة القراءة</a></section>{/if}
      <section class="landing-tools"><a href="/mushaf"><span class="quick-icon">ق</span><strong>المصحف والقراءة</strong><small>فهرس السور والآيات</small></a><a href="/search"><span class="quick-icon">⌕</span><strong>البحث القرآني</strong><small>ابحث باسم السورة أو الموضوع</small></a><a href="/tafsir"><span class="quick-icon">ت</span><strong>التفسير والترجمة</strong><small>افهم الآية في سياقها</small></a><a href="/favorites"><span class="quick-icon">★</span><strong>المحفوظات</strong><small>{favorites.length} آية محفوظة</small></a></section>
      <section class="landing-contact" id="contact"><div><span class="section-label">تواصل معنا</span><h2>نحن قريبون منك</h2><p>للاستفسارات أو المقترحات، تواصل معنا مباشرة عبر واتساب أو البريد الإلكتروني.</p></div><div class="contact-actions"><a class="contact-action whatsapp" href="https://wa.me/201283865399" target="_blank" rel="noreferrer"><span>◌</span><strong>واتساب</strong><small>محادثة مباشرة</small></a><a class="contact-action email" href="mailto:dyba8561@gmail.com"><span>@</span><strong>البريد الإلكتروني</strong><small>dyba8561@gmail.com</small></a></div></section>
    {/if}

    {#if currentPage === "search"}
    <section class="assistant-panel">
      <div class="assistant-copy">
        <span class="section-label">مساعد البحث الذكي</span>
        <h2>اسأل عن موضوع قرآني</h2>
        <p>يبحث في النص القرآني الموثق ويعرض الآيات المرتبطة بسؤالك، مع الحفاظ على المصدر واضحًا.</p>
      </div>
      <form class="assistant-form" onsubmit={(event) => { event.preventDefault(); askAssistant(); }}>
        <input bind:value={assistantQuery} placeholder="مثال: آيات عن الصبر والرحمة" aria-label="سؤال البحث الذكي" />
        <button type="submit">ابدأ البحث</button>
      </form>
      <div class="suggestion-row">
        {#each ["الصبر", "الرحمة", "قيام الليل", "بر الوالدين"] as suggestion}
          <button type="button" onclick={() => { assistantQuery = suggestion; askAssistant(); }}>{suggestion}</button>
        {/each}
      </div>
    </section>
    {/if}

    {#if currentPage === "search"}
      <section class="search-center-panel"><div class="search-scope" role="tablist"><span>ابحث في:</span>{#each [{ id: "all", label: "كل الموقع" }, { id: "quran", label: "القرآن" }, { id: "adhkar", label: "الأذكار والأدوات" }] as scope}<button class:active={searchScope === scope.id} type="button" onclick={() => searchScope = scope.id}>{scope.label}</button>{/each}</div>{#if siteSearchResults.length}<div class="site-results">{#each siteSearchResults as item}<a href={item.href}><span>{item.type}</span><strong>{item.title}</strong><small>{item.text}</small></a>{/each}</div>{:else if query}<div class="search-empty">لا توجد نتائج في الأقسام المحلية لهذا البحث.</div>{/if}</section>
    {/if}

    {#if currentPage === "tasbih"}
      <section class="special-page tasbih-page"><span class="section-label">ذكر متسلسل {tasbihIndex + 1} من {tasbihItems.length}</span><h2>السبحة الإلكترونية</h2><p>اضغط على الدائرة. عند اكتمال العدد ينتقل الموقع تلقائيًا إلى الذكر التالي.</p><div class="tasbih-current"><strong>{tasbihItems[tasbihIndex].title}</strong><span>{tasbihItems[tasbihIndex].text}</span></div><div class="tasbih-counter" role="button" tabindex="0" aria-label="زيادة عداد التسبيح" onclick={incrementTasbih} onkeydown={(event) => event.key === "Enter" && incrementTasbih()}><span>{tasbihCount}</span><small>من {tasbihTarget}</small></div><div class="tasbih-controls"><button type="button" onclick={resetTasbih}>إعادة الدورة</button></div></section>
    {:else if currentPage === "adhkar"}
      <section class="special-page adhkar-page"><span class="section-label">الذكر اليومي</span><h2>أذكار المسلم</h2><p>اختر القسم واقرأ الذكر بهدوء، مع مصدر واضح للمحتوى المعروض.</p><div class="dhikr-tabs">{#each dhikrItems as item, index}<button class:active={selectedDhikr === index} type="button" onclick={() => selectedDhikr = index}>{item.title}</button>{/each}</div><article class="dhikr-card"><span class="dhikr-mark">ذِكر</span><p>{dhikrItems[selectedDhikr].text}</p><button type="button" onclick={() => copyAyah(dhikrItems[selectedDhikr].text)}>نسخ الذكر</button></article></section>
    {:else if currentPage === "translations"}
      <section class="special-page tool-page"><span class="section-label">ترجمات القرآن</span><h2>قارن المعنى بين اللغات</h2><p>افتح آية من صفحة القرآن ثم استخدم تبويب الترجمات لعرض النص الإنجليزي المساند بجانب الآية العربية.</p><a class="primary-action" href="/quran">ابدأ من قارئ القرآن <span>←</span></a></section>
    {:else if currentPage === "favorites"}
      <section class="special-page favorites-page"><span class="section-label">مكتبتك الخاصة</span><h2>الآيات المحفوظة</h2><p>احتفظ بالآيات التي تريد الرجوع إليها بسهولة. تحفظ هذه القائمة على جهازك فقط.</p>{#if favorites.length}<div class="favorite-list">{#each favorites as item}<a class="favorite-item" href={`/quran?ayah=${item}`}><span class="favorite-star">★</span><span><strong>الآية {item}</strong><small>فتح الآية في القارئ</small></span><span class="favorite-arrow">←</span></a>{/each}</div>{:else}<div class="empty-state favorites-empty"><strong>لا توجد آيات محفوظة</strong><span>ابدأ القراءة واضغط «حفظ» لتظهر آياتك هنا.</span><a class="outline-button" href="/quran">اذهب إلى القرآن</a></div>{/if}</section>
    {/if}

    {#if isReaderPage() && !currentSurah}
      <section class="surah-page-panel quran-index-launcher"><div class="panel-toolbar"><div><span class="section-label">قارئ القرآن</span><h2>اختر السورة من القائمة الجانبية</h2><p>افتح الفهرس للتصفح السريع بين السور والبدء بالقراءة.</p></div><button class="open-index-button" type="button" onclick={() => showSurahs = true}>فتح فهرس السور</button></div>{#if surahsLoading}<div class="empty-state">جاري تحميل فهرس السور...</div>{/if}</section>
    {/if}

    {#if isReaderPage() && currentSurah}
      <section class="full-surah-panel">
        <div class="surah-reader-head"><button class="open-index-button" type="button" onclick={() => showSurahs = true}>☰ الفهرس</button><div><span class="section-label">سورة {currentSurah.name}</span><h2>{currentSurah.englishName}</h2><small>{currentSurah.revelationType === "Meccan" ? "مكية" : "مدنية"} · {currentSurah.numberOfAyahs} آية</small></div><button class="open-index-button" type="button" onclick={() => { currentSurah = null; }}>تغيير السورة</button></div>
        <div class="surah-navigation"><button type="button" onclick={() => navigateSurah(-1)} disabled={currentSurah.number === 1}>السورة السابقة</button><button type="button" onclick={() => navigateSurah(1)} disabled={currentSurah.number === 114}>السورة التالية</button></div>
        {#if surahLoading}<div class="empty-state">جاري تحميل السورة...</div>{:else}<div class="full-ayah-list">{#each currentSurah.ayahs as verse}<article class="full-ayah"><span class="full-ayah-number">{verse.numberInSurah}</span><p>{verse.text}</p><div><button type="button" onclick={() => { reference = `${currentSurah?.number}:${verse.numberInSurah}`; toggleFavorite(); }}>☆ حفظ</button><a href={`https://quran.com/${currentSurah.number}/${verse.numberInSurah}`} target="_blank" rel="noreferrer">المصدر ↗</a></div></article>{/each}</div>{/if}
      </section>
    {/if}

    {#if ["search", "tafsir", "translation", "hadith"].includes(currentPage) || (isReaderPage() && ayah)}
    <div class="content-tabs" role="tablist">{#each ["القرآن", "التفسير", "الترجمات", "الأحاديث"] as tab}<button class:active={activeTab === tab} type="button" onclick={() => { activeTab = tab; if (tab === "التفسير") loadStudyData("tafsir"); if (tab === "الترجمات") loadStudyData("translation"); }}>{tab}</button>{/each}</div>

    {#if activeTab === "القرآن" && (!isReaderPage() || ayah)}
      <section class="reading-panel"><div class="panel-toolbar"><span class="section-label">القراءة اليومية</span><span class="result-note">{message}</span><div class="reading-tools"><button type="button" aria-label="تصغير الخط" onclick={() => adjustFont(-0.05)}>A−</button><button type="button" aria-label="تكبير الخط" onclick={() => adjustFont(0.05)}>A+</button></div></div>
        {#if loading}<div class="empty-state">جاري التحميل...</div>
        {:else if ayah}<article class="ayah-card"><div class="ayah-meta"><span>{ayah.surah?.name}</span><span>{reference}</span></div><p class="ayah-text" style={`font-size: calc(clamp(2rem, 4vw, 3.2rem) * ${fontScale})`}>{ayah.text}</p><div class="ayah-actions"><button type="button" onclick={toggleFavorite}>{favorites.includes(reference) ? "★ محفوظة" : "☆ حفظ"}</button><button type="button" onclick={() => copyAyah(ayah?.text || "")}>نسخ الآية</button><button type="button" onclick={() => shareAyah(ayah?.text || "")}>مشاركة</button><a href={`https://quran.com/${reference.replace(":", "/")}`} target="_blank" rel="noreferrer">المصدر ↗</a></div><div class="ayah-footer"><span>نص القرآن الكريم</span><span>آخر قراءة محفوظة تلقائيًا</span></div></article>
        {:else if results.length}<div class="search-results"><div class="search-results-heading"><strong>نتائج البحث</strong><span>اضغط على أي نتيجة لفتح الآية كاملة</span></div>{#each visibleResults as item}<button class="search-result" type="button" onclick={() => chooseResult(item)}><span>{item.surah.name} · الآية {item.numberInSurah}</span><strong>{item.text}</strong><small>فتح الآية في القارئ ←</small></button>{/each}{#if visibleResults.length < results.length}<button class="load-more" type="button" onclick={showMoreResults}>عرض نتائج إضافية ({results.length - visibleResults.length})</button>{/if}</div>
        {:else}<div class="empty-state">{message}</div>{/if}
      </section>
    {:else if activeTab === "التفسير"}
      <section class="reading-panel informational" id="tafsir"><span class="section-label">تفسير الميسر</span><h2>افهم الآية في سياقها</h2>{#if loading}<div class="empty-state">جاري تحميل التفسير...</div>{:else}<p class="study-text">{tafsirText || "اختر آية ثم افتح تبويب التفسير لعرض المعنى الميسر."}</p>{/if}<a class="outline-button" href="/documentation">استكشاف مصادر التفسير</a></section>
    {:else if activeTab === "الترجمات"}
      <section class="reading-panel informational"><span class="section-label">English translation</span><h2>ترجمة الآية</h2>{#if loading}<div class="empty-state">جاري تحميل الترجمة...</div>{:else}<p class="study-text translation-text">{translationText || "اختر آية ثم افتح تبويب الترجمات لعرض الترجمة."}</p>{/if}</section>
    {:else}
      <section class="reading-panel hadith-library informational" id="hadith"><div class="hadith-heading"><div><span class="section-label">مختارات الحديث</span><h2>أحاديث قصيرة في موضوعات متنوعة</h2><p>مجموعة مختارة للقراءة اليومية، مع تصنيف ومصدر مختصر لكل حديث.</p></div><span class="hadith-count">{visibleHadith.length} من {hadithItems.length}</span></div><div class="hadith-filters" role="tablist" aria-label="تصنيف الأحاديث">{#each hadithTopics as topic}<button class:active={hadithTopic === topic} type="button" onclick={() => hadithTopic = topic}>{topic}</button>{/each}</div><div class="hadith-grid">{#each visibleHadith as item, index}<article class="hadith-card"><div class="hadith-card-top"><span class="hadith-number">{String(index + 1).padStart(2, "0")}</span><span class="hadith-topic">{item.topic}</span></div><p>{item.text}</p><div class="hadith-card-footer"><small>{item.source}</small><button type="button" onclick={() => copyHadith(item)}>نسخ الحديث</button></div></article>{/each}</div></section>
    {/if}

    {/if}

    {#if isKnownPage() && currentPage !== "home" && !["tasbih", "adhkar", "mushaf", "translations", "favorites"].includes(currentPage)}
    <section class="feature-strip"><div><span>01</span><strong>قرآن موثوق</strong><p>نص عربي من مصدر مرجعي واضح.</p></div><div><span>02</span><strong>بحث سريع</strong><p>اعثر على الآية بالمرجع أو الكلمة.</p></div><div><span>03</span><strong>تفسير قابل للتوسع</strong><p>مصمم لإضافة المدارس والمصادر.</p></div></section>
    {/if}
  </main>

  <footer class="app-footer"><span>Rushd — رُشد</span><span>المالك وصانع الموقع: أحمد ديب</span><a href="mailto:dyba8561@gmail.com">تواصل معي</a><a href="mailto:dyba8561@gmail.com">dyba8561@gmail.com</a><a href="tel:01283865399">01283865399</a></footer>
  {#if copyNotice}<div class="toast" role="status">{copyNotice}</div>{/if}
  <nav class="mobile-nav" aria-label="التنقل الرئيسي"><a class:active={currentPage === "home"} href="/"><span>⌂</span>الرئيسية</a><a class:active={isReaderPage()} href="/mushaf"><span>ق</span>المصحف</a><a class:active={currentPage === "search"} href="/search"><span>⌕</span>بحث</a><a class:active={currentPage === "favorites"} href="/favorites"><span>★</span>محفوظات</a></nav>
</div>
