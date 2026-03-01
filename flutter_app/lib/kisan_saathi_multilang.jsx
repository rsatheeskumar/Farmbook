import { useState, useEffect, useRef } from "react";

// ─────────────────────────────────────────────────────────
// LANGUAGE & STATE CONFIG
// ─────────────────────────────────────────────────────────
const LANGUAGES = {
  mr: {
    code: "mr",
    name: "मराठी",
    state: "Maharashtra",
    stateNative: "महाराष्ट्र",
    flag: "🟠",
    font: "'Noto Sans Devanagari', sans-serif",
    ui: {
      appTagline: "तुमचा AI शेती मित्र",
      welcome: "स्वागत आहे",
      chooseState: "तुमचे राज्य निवडा",
      chooseLanguage: "भाषा निवडा",
      phone: "📱 फोन नंबर *",
      name: "👤 आपले नाव",
      village: "🏘 गाव *",
      crop: "🌱 पीक",
      soil: "🪨 माती",
      soilTypes: ["काळी", "लाल", "वालुकामय"],
      irrigation: "💧 पाण्याचा स्रोत",
      irrigationTypes: ["विहीर", "नळ", "ठिबक", "पाऊस"],
      startBtn: "✅ सुरू करा →",
      todayTask: "🌅 आजचे काम",
      listen: "🔊 ऐका",
      speaking: "● बोला...",
      thinking: "⏳ सल्ला येतो आहे...",
      tapToSpeak: "बोलण्यासाठी दाबा 👇",
      dailyAdvice: "आज सकाळी शेताला भेट द्या. पिकाच्या खालच्या पानांवर लक्ष ठेवा — कीड लवकर तिथेच दिसते.",
      rain: "पाऊस",
      photoLabel: "📸 पीक फोटो",
    },
    responses: {
      "पाणी": "आज पाणी देऊ नका. उद्या ७०% पाऊस येण्याची शक्यता आहे. पाणी दिल्यास मुळं कुजण्याचा धोका आहे.",
      "खत": "पाऊस थांबल्यावर युरिया द्या. ओल्या जमिनीत खत दिल्यास वाहून जाते आणि पैसे वाया जातात.",
      "फवारणी": "आज फवारणी करू नका, वारा जास्त आहे. उद्या सकाळी ७ वाजेपूर्वी फवारणी करा.",
      "पिवळी": "पानं पिवळी पडणे म्हणजे नायट्रोजनची कमतरता. एकरी १० किलो युरिया द्या.",
      "कापणी": "अजून १५-२० दिवस थांबा. आत्ता पाणी बंद करा म्हणजे दाणे चांगले भरतील.",
    },
    sampleQ: ["आज पाणी द्यायचं का?", "खत कधी घालायचं?", "पानं पिवळी पडत आहेत", "फवारणी करायची का?", "कापणी कधी होईल?"],
    photoResponse: "पानांवर करपा रोग दिसतो. उद्या सकाळी मॅन्कोझेब फवारा. एकरी २ लिटर पाण्यात मिसळा.",
    defaultResponse: (crop, village) => `${village} मध्ये ${crop} साठी आज हवामान ठीक आहे. काही समस्या दिसल्यास फोटो पाठवा.`,
    theme: { primary: "#2e7d32", dark: "#1b5e20", light: "#e8f5e9", accent: "#ff6f00" },
  },

  ta: {
    code: "ta",
    name: "தமிழ்",
    state: "Tamil Nadu",
    stateNative: "தமிழ்நாடு",
    flag: "🔴",
    font: "'Noto Sans Tamil', sans-serif",
    ui: {
      appTagline: "உங்கள் AI விவசாய நண்பர்",
      welcome: "வரவேற்கிறோம்",
      chooseState: "உங்கள் மாநிலத்தை தேர்ந்தெடுக்கவும்",
      chooseLanguage: "மொழியை தேர்ந்தெடுக்கவும்",
      phone: "📱 தொலைபேசி *",
      name: "👤 உங்கள் பெயர்",
      village: "🏘 கிராமம் *",
      crop: "🌱 பயிர்",
      soil: "🪨 மண் வகை",
      soilTypes: ["கருப்பு", "சிவப்பு", "மணல்"],
      irrigation: "💧 நீர் ஆதாரம்",
      irrigationTypes: ["கிணறு", "குழாய்", "சொட்டு", "மழை"],
      startBtn: "✅ தொடங்கு →",
      todayTask: "🌅 இன்றைய பணி",
      listen: "🔊 கேளு",
      speaking: "● பேசுங்கள்...",
      thinking: "⏳ ஆலோசனை வருகிறது...",
      tapToSpeak: "பேச அழுத்துங்கள் 👇",
      dailyAdvice: "இன்று காலை வயலுக்கு செல்லுங்கள். கீழ் இலைகளை கவனமாக பாருங்கள் — பூச்சி முதலில் அங்கே தென்படும்.",
      rain: "மழை",
      photoLabel: "📸 பயிர் புகைப்படம்",
    },
    responses: {
      "தண்ணீர்": "இன்று தண்ணீர் பாய்ச்சாதீர்கள். நாளை 70% மழை வாய்ப்பு உள்ளது. வேர் அழுகும் அபாயம் உள்ளது.",
      "உரம்": "மழை நின்றபின் யூரியா போடுங்கள். ஈரமான மண்ணில் உரம் போட்டால் வீணாகும்.",
      "மஞ்சள்": "இலை மஞ்சளாவது நைட்ரஜன் குறைபாடு. ஏக்கருக்கு 10 கிலோ யூரியா கொடுங்கள்.",
      "அறுவடை": "இன்னும் 15-20 நாட்கள் காத்திருங்கள். இப்போது தண்ணீர் நிறுத்துங்கள்.",
      "பூச்சி": "இலைகளில் அசுவினி தாக்குதல் உள்ளது. இன்று மாலை இமிடாக்லோப்ரிட் தெளிக்கவும்.",
    },
    sampleQ: ["இன்று தண்ணீர் பாய்ச்சலாமா?", "உரம் எப்போது போடுவது?", "இலைகள் மஞ்சளாகின்றன", "பூச்சி மருந்து அடிக்கலாமா?", "அறுவடை எப்போது?"],
    photoResponse: "இலைகளில் கருகல் நோய் தெரிகிறது. நாளை காலை மேன்கோசெப் தெளிக்கவும். ஒரு லிட்டர் தண்ணீரில் 2 கிராம் கலக்கவும்.",
    defaultResponse: (crop, village) => `${village} இல் ${crop} பயிருக்கு இன்று வானிலை சரியாக உள்ளது. பிரச்னை இருந்தால் படம் அனுப்புங்கள்.`,
    theme: { primary: "#b71c1c", dark: "#7f0000", light: "#ffebee", accent: "#e65100" },
  },

  en: {
    code: "en",
    name: "English",
    state: "All States",
    stateNative: "All India",
    flag: "🔵",
    font: "'Georgia', serif",
    ui: {
      appTagline: "Your AI Farm Companion",
      welcome: "Welcome",
      chooseState: "Choose your State",
      chooseLanguage: "Choose Language",
      phone: "📱 Phone Number *",
      name: "👤 Your Name",
      village: "🏘 Village *",
      crop: "🌱 Crop",
      soil: "🪨 Soil Type",
      soilTypes: ["Black", "Red", "Sandy"],
      irrigation: "💧 Water Source",
      irrigationTypes: ["Well", "Canal", "Drip", "Rain"],
      startBtn: "✅ Get Started →",
      todayTask: "🌅 Today's Action",
      listen: "🔊 Listen",
      speaking: "● Speaking...",
      thinking: "⏳ Getting advice...",
      tapToSpeak: "Tap to speak 👇",
      dailyAdvice: "Visit your field this morning. Check the lower leaves carefully — pests usually appear there first.",
      rain: "Rain",
      photoLabel: "📸 Crop Photo",
    },
    responses: {
      "water": "Don't irrigate today. 70% chance of rain in 24 hours. Watering now risks root rot.",
      "fertilizer": "Apply urea after rain stops. Fertilizer washes away in wet soil and wastes money.",
      "yellow": "Yellow leaves indicate nitrogen deficiency. Apply 10kg urea per acre. You'll see improvement in 5 days.",
      "harvest": "Wait 15-20 more days. Stop watering now so grains fill well and yield improves.",
      "pest": "Aphid infestation on leaves. Spray imidacloprid this evening. Check again in 10 days.",
    },
    sampleQ: ["Should I water today?", "When to apply fertilizer?", "Leaves turning yellow", "Should I spray pesticide?", "When is harvest time?"],
    photoResponse: "Leaf blight disease detected. Spray Mancozeb tomorrow morning. Mix 2g per litre of water.",
    defaultResponse: (crop, village) => `Weather looks good for ${crop} in ${village} today. Send a photo if you notice any problems.`,
    theme: { primary: "#1565c0", dark: "#0d47a1", light: "#e3f2fd", accent: "#f57f17" },
  },
};

const STATES = [
  { name: "Maharashtra", native: "महाराष्ट्र", lang: "mr", emoji: "🟠", crops: "Cotton, Soybean, Sugarcane" },
  { name: "Tamil Nadu",  native: "தமிழ்நாடு",  lang: "ta", emoji: "🔴", crops: "Paddy, Banana, Groundnut" },
  { name: "Other / English", native: "All India", lang: "en", emoji: "🔵", crops: "All crops" },
];

// ─────────────────────────────────────────────────────────
// MAIN APP
// ─────────────────────────────────────────────────────────
export default function KisanSaathi() {
  const [step, setStep] = useState("language"); // language | register | home
  const [lang, setLang] = useState(null);
  const [farmData, setFarmData] = useState(null);
  const [form, setForm] = useState({ phone: "", name: "", village: "", crop: "", soil: "", irrigation: "" });
  const [isRecording, setIsRecording] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [currentQ, setCurrentQ] = useState(null);
  const [pulse, setPulse] = useState(false);
  const recordTimer = useRef(null);
  const qIndex = useRef(0);
  const chatEnd = useRef(null);

  const L = lang ? LANGUAGES[lang] : null;

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation]);

  useEffect(() => {
    let t;
    if (isRecording) t = setInterval(() => setPulse(p => !p), 500);
    return () => clearInterval(t);
  }, [isRecording]);

  function selectLanguage(langCode) {
    setLang(langCode);
    setStep("register");
  }

  function handleRegister() {
    if (!form.phone || !form.village) return;
    setFarmData({ ...form, lang });
    setStep("home");
  }

  function handleMic() {
    if (isThinking) return;
    if (isRecording) {
      stopAndProcess();
    } else {
      setIsRecording(true);
      recordTimer.current = setTimeout(stopAndProcess, 5000);
    }
  }

  function stopAndProcess() {
    clearTimeout(recordTimer.current);
    setIsRecording(false);
    const questions = L.sampleQ;
    const q = questions[qIndex.current % questions.length];
    qIndex.current++;
    setCurrentQ(q);
    setIsThinking(true);

    setTimeout(() => {
      const responses = L.responses;
      const found = Object.entries(responses).find(([k]) =>
        q.toLowerCase().includes(k.toLowerCase())
      );
      const answer = found
        ? found[1]
        : L.defaultResponse(farmData?.crop || "crop", farmData?.village || "your village");

      setConversation(prev => [...prev, {
        q, a: answer,
        time: new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }),
      }]);
      setCurrentQ(null);
      setIsThinking(false);
    }, 2000);
  }

  function handlePhoto() {
    setConversation(prev => [...prev, {
      q: L.ui.photoLabel,
      a: L.photoResponse,
      time: new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }),
    }]);
  }

  const theme = L?.theme || { primary: "#2e7d32", dark: "#1b5e20", light: "#e8f5e9", accent: "#ff6f00" };

  // ── LANGUAGE SELECTION SCREEN ──────────────────────────
  if (step === "language") {
    return (
      <div style={phoneStyle}>
        <div style={{ ...statusBar, background: "#1a1a2e" }}>
          <span style={{ color: "#aaa", fontSize: 12 }}>9:41</span>
          <span style={{ color: "#aaa", fontSize: 12 }}>📶 🔋</span>
        </div>

        {/* Hero */}
        <div style={{
          background: "linear-gradient(160deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
          padding: "32px 20px 28px",
          textAlign: "center",
        }}>
          <div style={{ fontSize: 52, marginBottom: 8 }}>🌾</div>
          <div style={{ fontSize: 26, fontWeight: 800, color: "#fff", letterSpacing: 1 }}>
            Kisan Saathi
          </div>
          <div style={{ fontSize: 13, color: "rgba(255,255,255,0.6)", marginTop: 4 }}>
            किसान साथी · கிசான் சாத்தி
          </div>
          <div style={{
            marginTop: 16,
            background: "rgba(255,255,255,0.08)",
            borderRadius: 12,
            padding: "10px 16px",
            fontSize: 13,
            color: "rgba(255,255,255,0.7)",
          }}>
            🇮🇳 AI Farm Advisor for Indian Farmers
          </div>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "20px 16px", background: "#f8f9fa" }}>
          <p style={{ fontSize: 15, color: "#555", fontWeight: 700, marginBottom: 14, textAlign: "center" }}>
            Choose your State & Language
          </p>

          {STATES.map(s => (
            <button
              key={s.lang}
              onClick={() => selectLanguage(s.lang)}
              style={{
                width: "100%",
                background: "white",
                border: "2px solid #e0e0e0",
                borderRadius: 16,
                padding: "16px 18px",
                marginBottom: 12,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 14,
                textAlign: "left",
                transition: "all 0.15s",
                boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = "#2e7d32"}
              onMouseLeave={e => e.currentTarget.style.borderColor = "#e0e0e0"}
            >
              <div style={{ fontSize: 36 }}>{s.emoji}</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 17, fontWeight: 800, color: "#1a1a1a" }}>
                  {s.name}
                </div>
                <div style={{ fontSize: 14, color: "#888", marginTop: 2 }}>
                  {s.native} · {LANGUAGES[s.lang].name}
                </div>
                <div style={{
                  marginTop: 6, fontSize: 11, color: "#aaa",
                  background: "#f5f5f5", borderRadius: 8,
                  padding: "3px 8px", display: "inline-block"
                }}>
                  🌾 {s.crops}
                </div>
              </div>
              <div style={{ fontSize: 20, color: "#ccc" }}>›</div>
            </button>
          ))}
        </div>
      </div>
    );
  }

  // ── REGISTRATION SCREEN ────────────────────────────────
  if (step === "register") {
    return (
      <div style={{ ...phoneStyle, fontFamily: L.font }}>
        <div style={{ ...statusBar, background: theme.dark }}>
          <span style={{ color: "rgba(255,255,255,0.8)", fontSize: 12 }}>9:41</span>
          <span style={{ color: "rgba(255,255,255,0.8)", fontSize: 12 }}>📶 🔋</span>
        </div>

        <div style={{
          background: `linear-gradient(135deg, ${theme.dark}, ${theme.primary})`,
          padding: "16px 18px",
          display: "flex", alignItems: "center", gap: 12,
        }}>
          <button onClick={() => setStep("language")} style={{
            background: "rgba(255,255,255,0.15)", border: "none",
            color: "white", borderRadius: 8, padding: "6px 10px",
            cursor: "pointer", fontSize: 16,
          }}>←</button>
          <div>
            <div style={{ color: "white", fontWeight: 700, fontSize: 17 }}>🌾 Kisan Saathi</div>
            <div style={{ color: "rgba(255,255,255,0.7)", fontSize: 12 }}>
              {LANGUAGES[lang].stateNative} · {LANGUAGES[lang].name}
            </div>
          </div>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "16px" }}>
          <div style={{ background: "white", borderRadius: 16, padding: 16, marginBottom: 14, boxShadow: "0 2px 12px rgba(0,0,0,0.07)" }}>
            <p style={{ fontSize: 14, color: "#555", fontWeight: 700, marginBottom: 10 }}>📋 {L.ui.welcome}</p>

            {[
              { key: "phone", label: L.ui.phone, type: "tel" },
              { key: "name", label: L.ui.name, type: "text" },
              { key: "village", label: L.ui.village, type: "text" },
              { key: "crop", label: L.ui.crop, type: "text" },
            ].map(f => (
              <div key={f.key}>
                <p style={{ fontSize: 13, color: "#777", marginBottom: 5, fontWeight: 600 }}>{f.label}</p>
                <input
                  type={f.type}
                  style={{
                    width: "100%", padding: "12px 14px", fontSize: 16,
                    border: `2px solid #e0e0e0`, borderRadius: 10, marginBottom: 10,
                    fontFamily: L.font, outline: "none", boxSizing: "border-box",
                  }}
                  value={form[f.key]}
                  onChange={e => setForm({ ...form, [f.key]: e.target.value })}
                  onFocus={e => e.target.style.borderColor = theme.primary}
                  onBlur={e => e.target.style.borderColor = "#e0e0e0"}
                />
              </div>
            ))}

            <p style={{ fontSize: 13, color: "#777", marginBottom: 8, fontWeight: 600 }}>{L.ui.soil}</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 12 }}>
              {L.ui.soilTypes.map(s => (
                <button key={s} onClick={() => setForm({ ...form, soil: s })}
                  style={{
                    padding: "9px 16px", borderRadius: 20, fontSize: 14, cursor: "pointer",
                    fontFamily: L.font, fontWeight: 600, transition: "all 0.15s",
                    background: form.soil === s ? theme.primary : "white",
                    color: form.soil === s ? "white" : "#555",
                    border: `2px solid ${form.soil === s ? theme.primary : "#ddd"}`,
                  }}>
                  {s}
                </button>
              ))}
            </div>

            <p style={{ fontSize: 13, color: "#777", marginBottom: 8, fontWeight: 600 }}>{L.ui.irrigation}</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 4 }}>
              {L.ui.irrigationTypes.map(s => (
                <button key={s} onClick={() => setForm({ ...form, irrigation: s })}
                  style={{
                    padding: "9px 16px", borderRadius: 20, fontSize: 14, cursor: "pointer",
                    fontFamily: L.font, fontWeight: 600, transition: "all 0.15s",
                    background: form.irrigation === s ? theme.primary : "white",
                    color: form.irrigation === s ? "white" : "#555",
                    border: `2px solid ${form.irrigation === s ? theme.primary : "#ddd"}`,
                  }}>
                  {s}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleRegister}
            style={{
              width: "100%", padding: "18px", fontSize: 19, fontWeight: 800,
              background: form.phone && form.village ? theme.primary : "#ccc",
              color: "white", border: "none", borderRadius: 14,
              cursor: form.phone && form.village ? "pointer" : "not-allowed",
              fontFamily: L.font, marginBottom: 20,
              boxShadow: form.phone && form.village ? `0 6px 20px ${theme.primary}55` : "none",
            }}>
            {L.ui.startBtn}
          </button>
        </div>
      </div>
    );
  }

  // ── HOME / VOICE SCREEN ────────────────────────────────
  return (
    <div style={{ ...phoneStyle, fontFamily: L.font }}>
      {/* Status bar */}
      <div style={{ ...statusBar, background: theme.dark }}>
        <span style={{ color: "rgba(255,255,255,0.8)", fontSize: 12 }}>9:41</span>
        <span style={{ color: "rgba(255,255,255,0.8)", fontSize: 12 }}>📶 🔋</span>
      </div>

      {/* Header */}
      <div style={{
        background: `linear-gradient(135deg, ${theme.dark}, ${theme.primary})`,
        padding: "12px 16px",
        display: "flex", justifyContent: "space-between", alignItems: "center",
      }}>
        <div>
          <div style={{ fontSize: 17, fontWeight: 800, color: "#fff" }}>🌾 Kisan Saathi</div>
          <div style={{ fontSize: 12, color: "rgba(255,255,255,0.7)", marginTop: 2 }}>
            {farmData?.village} · {farmData?.crop || "—"} · {LANGUAGES[lang].name}
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <div style={{
            background: "rgba(255,255,255,0.15)", color: "white",
            fontSize: 11, padding: "5px 10px", borderRadius: 20, fontWeight: 700,
          }}>
            ☁️ 32°C · 65% {L.ui.rain}
          </div>
          <button onClick={() => setStep("language")} style={{
            background: "rgba(255,255,255,0.15)", border: "none",
            color: "white", borderRadius: 8, padding: "5px 8px",
            cursor: "pointer", fontSize: 13,
          }} title="Change language">🌐</button>
        </div>
      </div>

      {/* Chat area */}
      <div style={{ flex: 1, overflowY: "auto", padding: "12px 14px", background: `${theme.light}88` }}>

        {/* Daily advice */}
        <div style={{
          background: `linear-gradient(135deg, ${theme.dark}, ${theme.primary})`,
          borderRadius: 16, padding: 16, marginBottom: 14, color: "white",
        }}>
          <div style={{ fontSize: 12, opacity: 0.75, marginBottom: 6, fontWeight: 700 }}>
            {L.ui.todayTask}
          </div>
          <div style={{ fontSize: 16, fontWeight: 600, lineHeight: 1.55 }}>
            {L.ui.dailyAdvice}
          </div>
          <button style={{
            marginTop: 10, background: "rgba(255,255,255,0.2)",
            border: "none", color: "white", padding: "7px 14px",
            borderRadius: 20, fontSize: 13, cursor: "pointer",
            fontFamily: L.font, fontWeight: 700,
          }}>
            {L.ui.listen}
          </button>
        </div>

        {/* Conversation */}
        {conversation.map((c, i) => (
          <div key={i} style={{ marginBottom: 14 }}>
            <div style={{
              background: "white", borderRadius: "14px 14px 14px 3px",
              padding: "10px 14px", maxWidth: "80%",
              boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
            }}>
              <div style={{ fontSize: 11, color: "#aaa", marginBottom: 3 }}>🎤 {c.time}</div>
              <div style={{ fontSize: 15, color: "#333" }}>{c.q}</div>
            </div>
            <div style={{
              background: theme.light, border: `1.5px solid ${theme.primary}33`,
              borderRadius: "14px 14px 3px 14px",
              padding: "12px 14px", marginLeft: "auto", maxWidth: "90%",
              marginTop: 6, boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
            }}>
              <div style={{ fontSize: 17, fontWeight: 600, lineHeight: 1.55, color: "#1a1a1a" }}>
                {c.a}
              </div>
              <button style={{
                marginTop: 8, background: theme.primary, border: "none",
                color: "white", padding: "6px 12px", borderRadius: 16,
                fontSize: 12, cursor: "pointer", fontFamily: L.font, fontWeight: 700,
              }}>
                {L.ui.listen}
              </button>
            </div>
          </div>
        ))}

        {/* Thinking */}
        {isThinking && (
          <div style={{ marginBottom: 14 }}>
            <div style={{
              background: "white", borderRadius: "14px 14px 14px 3px",
              padding: "10px 14px", maxWidth: "80%", boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
            }}>
              <div style={{ fontSize: 15, color: "#333" }}>🎤 {currentQ}</div>
            </div>
            <div style={{
              background: theme.light, borderRadius: "14px 14px 3px 14px",
              padding: "14px", marginLeft: "auto", maxWidth: "60%",
              marginTop: 6, display: "flex", alignItems: "center", gap: 10,
            }}>
              <ThinkingDots color={theme.primary} />
              <span style={{ fontSize: 13, color: "#888" }}>{L.ui.thinking}</span>
            </div>
          </div>
        )}
        <div ref={chatEnd} />
      </div>

      {/* Bottom controls */}
      <div style={{
        background: "white", borderTop: "1px solid #eee",
        padding: "10px 16px 14px",
        boxShadow: "0 -4px 20px rgba(0,0,0,0.06)",
      }}>
        <div style={{ textAlign: "center", height: 20, marginBottom: 10 }}>
          <span style={{
            fontSize: 13, fontWeight: 600,
            color: isRecording ? "#c62828" : isThinking ? theme.primary : "#999",
          }}>
            {isRecording ? L.ui.speaking : isThinking ? L.ui.thinking : L.ui.tapToSpeak}
          </span>
        </div>

        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 20 }}>
          {/* Photo */}
          <button onClick={handlePhoto} style={{
            width: 52, height: 52, borderRadius: "50%",
            background: "#f5f5f5", border: "2px solid #e0e0e0",
            fontSize: 22, cursor: "pointer",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>📸</button>

          {/* MIC */}
          <button
            onClick={handleMic}
            disabled={isThinking}
            style={{
              width: 80, height: 80, borderRadius: "50%", border: "none",
              fontSize: 32, cursor: isThinking ? "not-allowed" : "pointer",
              color: "white",
              background: isRecording ? "#c62828" : isThinking ? "#bbb" : theme.primary,
              boxShadow: isRecording
                ? "0 0 0 10px rgba(198,40,40,0.15), 0 6px 20px rgba(198,40,40,0.4)"
                : `0 6px 24px ${theme.primary}66`,
              transform: isRecording && pulse ? "scale(1.08)" : "scale(1)",
              transition: "all 0.25s",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
            {isThinking ? "⏳" : isRecording ? "⏹" : "🎤"}
          </button>

          {/* Clear */}
          <button onClick={() => setConversation([])} style={{
            width: 52, height: 52, borderRadius: "50%",
            background: "#f5f5f5", border: "2px solid #e0e0e0",
            fontSize: 20, cursor: "pointer",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>🗑</button>
        </div>
      </div>
    </div>
  );
}

function ThinkingDots({ color }) {
  const [dot, setDot] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setDot(d => (d + 1) % 3), 400);
    return () => clearInterval(t);
  }, []);
  return (
    <div style={{ display: "flex", gap: 5 }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          width: 9, height: 9, borderRadius: "50%",
          background: i === dot ? color : "#ddd",
          transition: "background 0.2s",
        }} />
      ))}
    </div>
  );
}

const phoneStyle = {
  width: 375, height: 720, margin: "0 auto",
  background: "#f8f9fa",
  borderRadius: 36,
  boxShadow: "0 24px 80px rgba(0,0,0,0.22), inset 0 0 0 2px rgba(255,255,255,0.2)",
  display: "flex", flexDirection: "column", overflow: "hidden",
  position: "relative",
};

const statusBar = {
  display: "flex", justifyContent: "space-between",
  padding: "6px 20px", fontSize: 12,
};
