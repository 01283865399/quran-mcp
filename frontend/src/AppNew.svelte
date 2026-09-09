<script lang="ts">
  import { onMount } from "svelte";

  type Ayah = { number: number; text: string; surah?: { number: number; name: string }; numberInSurah?: number };
  type SearchMatch = { number: number; text: string; surah: { number: number; name: string }; numberInSurah: number };
  type Surah = { number: number; name: string; englishName: string; numberOfAyahs: number; revelationType: string };
  type SurahData = { number: number; name: string; englishName: string; numberOfAyahs: number; revelationType: string; ayahs: Ayah[] };

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
  let searchScope = $state("all");
  let siteSearchResults = $state<{ title: string; type: string; text: string; href: string }[]>([]);
  const searchPageSize = 6;
  const apiBase = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");
  const apiUrl = (path: string) => `${apiBase}${path}`;

  const visibleResults = $derived(results.slice(0, searchPage * searchPageSize));

  async function loadAyah(value = reference) {
    const normalized = value.trim();
    if (!/^\d{1,3}:\d{1,3}$/.test(normalized)) {
      message = "اكتب مرجعًا صحيحًا مثل 2:255";
      return;
    }
    loading = true;
    message = "جاري تحميل الآية...";
    try {
      const response = await fetch(apiUrl(`/api/quran?ayah=${encodeURIComponent(normalized)}`));
      const payload = await response.json();
      if (!response.ok || payload.code !== 200) throw new Error(payload.error);
      ayah = payload.data;
      results = [];
      currentSurah = null;
      localStorage.setItem("quran-last-reading", normalized);
      message = `سورة ${ayah?.surah?.name || "القرآن"} · الآية ${ayah?.numberInSurah || ""}`;
    } catch (error) {
      message = error instanceof Error ? error.message : "تعذر تحميل الآية";
    } finally {
      loading = false;
    }
  }

  async function searchQuran() {
    if (!query.trim()) return;
    if (searchScope === "quran") siteSearchResults = [];
    if (searchScope !== "quran") {
      runSiteSearch(query);
      if (searchScope === "adhkar") return;
    }
    loading = true;
    message = "جاري البحث في القرآن الكريم...";
    try {
      const response = await fetch(apiUrl(`/api/quran?search=${encodeURIComponent(query.trim())}`));
      const payload = await response.json();
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
    try {
      const response = await fetch(apiUrl("/.health"), { headers: { Accept: "application/json" } });
      backendStatus = response.ok ? "الخادم متصل" : "الخادم غير مكتمل";
    } catch {
      backendStatus = "الخادم غير متصل";
    }
  }

  async function loadSurahs() {
    surahsLoading = true;
    try {
      const response = await fetch(apiUrl("/api/surahs"));
      const payload = await response.json();
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
      const payload = await response.json();
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
      const payload = await response.json();
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
    const titles: Record<string, string> = { quran: "القرآن الكريم", search: "ابحث في القرآن", tafsir: "تفسير الآيات", hadith: "مكتبة الأحاديث", adhkar: "أذكار المسلم", tasbih: "السبحة الإلكترونية", mushaf: "أدوات المصحف", translations: "ترجمات القرآن" };
    return titles[currentPage] || "اقرأ، ابحث، وتدبّر";
  }

  function pageDescription() {
    const descriptions: Record<string, string> = { quran: "فهرس السور وقراءة واضحة مع حفظ موضعك ومفضلاتك.", search: "اكتب كلمة أو موضوعًا، وستظهر لك نتائج مختارة على دفعات سهلة القراءة.", tafsir: "اقرأ المعنى الميسر للآية مع الاحتفاظ بالنص والمصدر أمامك.", hadith: "مكتبة حديث موثقة قيد التجهيز بمصادرها الأصلية.", adhkar: "أذكار يومية مرتبة لتقرأها بهدوء وتحفظها في روتينك.", tasbih: "سبحة إلكترونية بسيطة تحفظ العدد على جهازك وتساعدك على الاستمرار.", mushaf: "مساحة منظمة لأدوات المصحف والقراءة والبحث في النص القرآني.", translations: "قارن ترجمة الآية مع النص العربي من داخل قارئ القرآن." };
    return descriptions[currentPage] || "وصول هادئ وموثوق إلى آيات القرآن الكريم، مع بحث سريع ومصادر قابلة للتوسع.";
  }

  onMount(() => {
    currentPage = window.location.pathname.replace("/", "") || "home";
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
    reference = localStorage.getItem("quran-last-reading") || reference;
    checkBackend();
    loadSurahs();
    if (!["quran", "search", "hadith"].includes(currentPage)) {
      loadAyah();
    }
    if (currentPage === "tafsir") loadStudyData("tafsir");
    if (currentPage === "translation") loadStudyData("translation");
  });
</script>

<div class:dark-mode={theme === "dark"} class="quran-app" dir="rtl">
  <header class="app-header">
    <a class="brand-wrap" href="/"><span class="brand-mark">ق</span><span class="brand-copy"><strong>قراني ديني</strong><small>رفيقك في تدبر القرآن</small></span></a>
    <nav class="app-nav"><a class:active={currentPage === "home"} href="/">الرئيسية</a><a class:active={currentPage === "quran"} href="/quran">القرآن</a><a class:active={currentPage === "search"} href="/search">البحث</a><a class:active={currentPage === "adhkar"} href="/adhkar">الأذكار</a><a class:active={currentPage === "tasbih"} href="/tasbih">السبحة</a><a href="/about">المزيد</a></nav>
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
      <div class="reader-actions">
        <form class="reference-form" onsubmit={(event) => { event.preventDefault(); loadAyah(); }}><label for="reference">انتقل إلى آية</label><div class="input-row"><input id="reference" bind:value={reference} placeholder="مثال: 2:255" /><button type="submit">فتح الآية</button></div></form>
        <form class="search-form" onsubmit={(event) => { event.preventDefault(); searchQuran(); }}><label for="search">ابحث في القرآن</label><div class="input-row"><input id="search" bind:value={query} placeholder="اكتب كلمة أو موضوعاً" /><button type="submit">بحث</button></div></form>
      </div>
    </section>

    {#if currentPage === "home"}
      <section class="welcome-strip">
        <div><span class="section-label">مساحتك اليومية</span><h2>اجعل للقرآن وقتًا في يومك</h2><p>ابدأ بآية، تابع وردك، ثم تعرّف على معناها من مصدر واضح.</p></div>
        <a class="primary-action" href="/quran">ابدأ القراءة <span>←</span></a>
      </section>
      <section class="quick-links">
        <a href="/quran"><span class="quick-icon">ق</span><strong>القرآن الكريم</strong><small>فهرس السور والقراءة</small></a>
        <a href="/search"><span class="quick-icon">⌕</span><strong>البحث الذكي</strong><small>ابحث في الآيات والموضوعات</small></a>
        <a href="/tafsir"><span class="quick-icon">ت</span><strong>التفسير</strong><small>افهم الآية في سياقها</small></a>
        <a href="/hadith"><span class="quick-icon">ح</span><strong>الأحاديث</strong><small>مصادر الحديث الموثوقة</small></a>
      </section>
    {/if}

    {#if currentPage === "home" || currentPage === "search"}
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
    {:else if currentPage === "mushaf"}
      <section class="special-page tool-page"><span class="section-label">أدوات القرآن</span><h2>المصحف التفاعلي</h2><p>هذه المساحة مخصصة لعرض صفحات المصحف والتصفح البصري، مع الحفاظ على نص القراءة والبحث في الموقع.</p><div class="tool-grid"><a href="/quran">القراءة النصية <small>فتح قارئ السور</small></a><a href="/search">البحث في الآيات <small>البحث الموضوعي</small></a><a href="/documentation">أدوات الخادم <small>التوثيق ومصادر البيانات</small></a></div></section>
    {:else if currentPage === "translations"}
      <section class="special-page tool-page"><span class="section-label">ترجمات القرآن</span><h2>قارن المعنى بين اللغات</h2><p>افتح آية من صفحة القرآن ثم استخدم تبويب الترجمات لعرض النص الإنجليزي المساند بجانب الآية العربية.</p><a class="primary-action" href="/quran">ابدأ من قارئ القرآن <span>←</span></a></section>
    {/if}

    {#if currentPage === "quran" && !currentSurah}
      <section class="surah-page-panel"><div class="panel-toolbar"><span class="section-label">فهرس القرآن الكريم</span><button class="open-index-button" type="button" onclick={() => showSurahs = true}>فتح القائمة الجانبية</button></div>{#if surahsLoading}<div class="empty-state">جاري تحميل فهرس السور...</div>{:else}<div class="surah-grid surah-page-grid">{#each surahs as surah}<button type="button" onclick={() => openSurah(surah)}><strong>{surah.number}. {surah.name}</strong><small>{surah.englishName} · {surah.numberOfAyahs} آية · {surah.revelationType === "Meccan" ? "مكية" : "مدنية"}</small></button>{/each}</div>{/if}</section>
    {/if}

    {#if currentPage === "quran" && currentSurah}
      <section class="full-surah-panel">
        <div class="surah-reader-head"><button class="open-index-button" type="button" onclick={() => showSurahs = true}>☰ الفهرس</button><div><span class="section-label">سورة {currentSurah.name}</span><h2>{currentSurah.englishName}</h2><small>{currentSurah.revelationType === "Meccan" ? "مكية" : "مدنية"} · {currentSurah.numberOfAyahs} آية</small></div><button class="open-index-button" type="button" onclick={() => { currentSurah = null; }}>تغيير السورة</button></div>
        <div class="surah-navigation"><button type="button" onclick={() => navigateSurah(-1)} disabled={currentSurah.number === 1}>السورة السابقة</button><button type="button" onclick={() => navigateSurah(1)} disabled={currentSurah.number === 114}>السورة التالية</button></div>
        {#if surahLoading}<div class="empty-state">جاري تحميل السورة...</div>{:else}<div class="full-ayah-list">{#each currentSurah.ayahs as verse}<article class="full-ayah"><span class="full-ayah-number">{verse.numberInSurah}</span><p>{verse.text}</p><div><button type="button" onclick={() => { reference = `${currentSurah?.number}:${verse.numberInSurah}`; toggleFavorite(); }}>☆ حفظ</button><a href={`https://quran.com/${currentSurah.number}/${verse.numberInSurah}`} target="_blank" rel="noreferrer">المصدر ↗</a></div></article>{/each}</div>{/if}
      </section>
    {/if}

    {#if !["tasbih", "adhkar", "mushaf", "translations"].includes(currentPage)}
    <div class="content-tabs" role="tablist">{#each ["القرآن", "التفسير", "الترجمات", "الأحاديث"] as tab}<button class:active={activeTab === tab} type="button" onclick={() => { activeTab = tab; if (tab === "التفسير") loadStudyData("tafsir"); if (tab === "الترجمات") loadStudyData("translation"); }}>{tab}</button>{/each}</div>

    {#if activeTab === "القرآن" && currentPage !== "quran"}
      <section class="reading-panel"><div class="panel-toolbar"><span class="section-label">القراءة اليومية</span><span class="result-note">{message}</span><div class="reading-tools"><button type="button" aria-label="تصغير الخط" onclick={() => adjustFont(-0.05)}>A−</button><button type="button" aria-label="تكبير الخط" onclick={() => adjustFont(0.05)}>A+</button></div></div>
        {#if loading}<div class="empty-state">جاري التحميل...</div>
        {:else if ayah}<article class="ayah-card"><div class="ayah-meta"><span>{ayah.surah?.name}</span><span>{reference}</span></div><p class="ayah-text" style={`font-size: calc(clamp(2rem, 4vw, 3.2rem) * ${fontScale})`}>{ayah.text}</p><div class="ayah-actions"><button type="button" onclick={toggleFavorite}>{favorites.includes(reference) ? "★ محفوظة" : "☆ حفظ"}</button><button type="button" onclick={() => copyAyah(ayah?.text || "")}>نسخ الآية</button><a href={`https://quran.com/${reference.replace(":", "/")}`} target="_blank" rel="noreferrer">المصدر ↗</a></div><div class="ayah-footer"><span>نص القرآن الكريم</span><span>آخر قراءة محفوظة تلقائيًا</span></div></article>
        {:else if results.length}<div class="search-results">{#each visibleResults as item}<button class="search-result" type="button" onclick={() => chooseResult(item)}><span>{item.surah.name} · {item.numberInSurah}</span><strong>{item.text}</strong></button>{/each}{#if visibleResults.length < results.length}<button class="load-more" type="button" onclick={showMoreResults}>عرض نتائج إضافية ({results.length - visibleResults.length})</button>{/if}</div>
        {:else}<div class="empty-state">{message}</div>{/if}
      </section>
    {:else if activeTab === "التفسير"}
      <section class="reading-panel informational" id="tafsir"><span class="section-label">تفسير الميسر</span><h2>افهم الآية في سياقها</h2>{#if loading}<div class="empty-state">جاري تحميل التفسير...</div>{:else}<p class="study-text">{tafsirText || "اختر آية ثم افتح تبويب التفسير لعرض المعنى الميسر."}</p>{/if}<a class="outline-button" href="/documentation">استكشاف مصادر التفسير</a></section>
    {:else if activeTab === "الترجمات"}
      <section class="reading-panel informational"><span class="section-label">English translation</span><h2>ترجمة الآية</h2>{#if loading}<div class="empty-state">جاري تحميل الترجمة...</div>{:else}<p class="study-text translation-text">{translationText || "اختر آية ثم افتح تبويب الترجمات لعرض الترجمة."}</p>{/if}</section>
    {:else}
      <section class="reading-panel informational" id="hadith"><span class="section-label">الأحاديث</span><h2>مكتبة الحديث قيد الإضافة</h2><p>الـ backend الحالي متخصص في القرآن والترجمات والتفسير ولا يحتوي قاعدة أحاديث بعد. الواجهة مجهزة لاستقبال مصدر حديث موثوق عند إضافته للمشروع.</p><a class="outline-button" href="/contact">اقترح مصدراً للحديث</a></section>
    {/if}

    {/if}

    {#if !["tasbih", "adhkar", "mushaf", "translations"].includes(currentPage)}
    <section class="feature-strip"><div><span>01</span><strong>قرآن موثوق</strong><p>نص عربي من مصدر مرجعي واضح.</p></div><div><span>02</span><strong>بحث سريع</strong><p>اعثر على الآية بالمرجع أو الكلمة.</p></div><div><span>03</span><strong>تفسير قابل للتوسع</strong><p>مصمم لإضافة المدارس والمصادر.</p></div></section>
    {/if}
  </main>

  <footer class="app-footer"><span>قراني ديني</span><span>المالك وصانع الموقع: أحمد ديب</span><a href="mailto:dyba8561@gmail.com">dyba8561@gmail.com</a><a href="tel:01283865399">01283865399</a></footer>
  {#if copyNotice}<div class="toast" role="status">{copyNotice}</div>{/if}
  <nav class="mobile-nav" aria-label="التنقل الرئيسي"><a class:active={currentPage === "home"} href="/"><span>⌂</span>الرئيسية</a><a class:active={currentPage === "quran"} href="/quran"><span>ق</span>القرآن</a><a class:active={currentPage === "search"} href="/search"><span>⌕</span>بحث</a><a class:active={currentPage === "tafsir"} href="/tafsir"><span>ت</span>تفسير</a></nav>
</div>
