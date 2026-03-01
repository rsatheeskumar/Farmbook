import { useState, useEffect, useRef } from "react";

const LANGS = {
  mr: {
    code: "mr", name: "मराठी", state: "महाराष्ट्र", flag: "🟠",
    font: "'Noto Sans Devanagari', sans-serif",
    theme: { primary: "#2e7d32", dark: "#1b5e20", light: "#e8f5e9", bubble: "#c8e6c9" },
    farmer: { name: "रामराव पाटील", village: "साखरवाडी", crop: "सोयाबीन" },
    daily: "आज सकाळी शेताला भेट द्या. पिकाच्या खालच्या पानांवर लक्ष ठेवा — कीड लवकर तिथेच दिसते.",
    tapLabel: "बोलण्यासाठी दाबा 👇",
    speakingLabel: "● बोला...",
    thinkingLabel: "⏳ सल्ला येतो आहे...",
    listenLabel: "🔊 ऐका",
    todayLabel: "🌅 आजचे काम",
    rainLabel: "पाऊस",
    questions: [
      "आज पाणी द्यायचं का?",
      "खत कधी घालायचं?",
      "पानं पिवळी पडत आहेत",
      "फवारणी करायची का?",
      "कापणी कधी होईल?",
    ],
    responses: [
      "आज पाणी देऊ नका. उद्या ७०% पाऊस येण्याची शक्यता आहे. पाणी दिल्यास मुळं कुजण्याचा धोका आहे.",
      "पाऊस थांबल्यावर युरिया द्या. ओल्या जमिनीत खत दिल्यास वाहून जाते आणि पैसे वाया जातात.",
      "पानं पिवळी पडणे म्हणजे नायट्रोजनची कमतरता. एकरी १० किलो युरिया द्या, ५ दिवसांत फरक दिसेल.",
      "आज फवारणी करू नका, वारा जास्त आहे. उद्या सकाळी ७ वाजेपूर्वी फवारणी करा.",
      "अजून १५-२० दिवस थांबा. आत्ता पाणी बंद करा म्हणजे दाणे चांगले भरतील.",
    ],
    photoResp: "पानांवर करपा रोग दिसतो. उद्या सकाळी मॅन्कोझेब फवारा. एकरी २ लिटर पाण्यात मिसळा.",
  },
  ta: {
    code: "ta", name: "தமிழ்", state: "தமிழ்நாடு", flag: "🔴",
    font: "'Noto Sans Tamil', sans-serif",
    theme: { primary: "#b71c1c", dark: "#7f0000", light: "#ffebee", bubble: "#ffcdd2" },
    farmer: { name: "முருகன் செல்வம்", village: "தஞ்சாவூர்", crop: "நெல்" },
    daily: "இன்று காலை வயலுக்கு செல்லுங்கள். கீழ் இலைகளை கவனமாக பாருங்கள் — பூச்சி முதலில் அங்கே தென்படும்.",
    tapLabel: "பேச அழுத்துங்கள் 👇",
    speakingLabel: "● பேசுங்கள்...",
    thinkingLabel: "⏳ ஆலோசனை வருகிறது...",
    listenLabel: "🔊 கேளு",
    todayLabel: "🌅 இன்றைய பணி",
    rainLabel: "மழை",
    questions: [
      "இன்று தண்ணீர் பாய்ச்சலாமா?",
      "உரம் எப்போது போடுவது?",
      "இலைகள் மஞ்சளாகின்றன",
      "பூச்சி மருந்து அடிக்கலாமா?",
      "அறுவடை எப்போது?",
    ],
    responses: [
      "இன்று தண்ணீர் பாய்ச்சாதீர்கள். நாளை 70% மழை வாய்ப்பு உள்ளது. வேர் அழுகும் அபாயம் உள்ளது.",
      "மழை நின்றபின் யூரியா போடுங்கள். ஈரமான மண்ணில் உரம் போட்டால் வீணாகும்.",
      "இலை மஞ்சளாவது நைட்ரஜன் குறைபாடு. ஏக்கருக்கு 10 கிலோ யூரியா கொடுங்கள்.",
      "இன்று மருந்து தெளிக்காதீர்கள், காற்று அதிகம். நாளை காலை 7 மணிக்கு முன் தெளிக்கவும்.",
      "இன்னும் 15-20 நாட்கள் காத்திருங்கள். இப்போது தண்ணீர் நிறுத்துங்கள்.",
    ],
    photoResp: "இலைகளில் கருகல் நோய் தெரிகிறது. நாளை காலை மேன்கோசெப் தெளிக்கவும். ஒரு லிட்டர் தண்ணீரில் 2 கிராம் கலக்கவும்.",
  },
  en: {
    code: "en", name: "English", state: "All India", flag: "🔵",
    font: "'Georgia', serif",
    theme: { primary: "#1565c0", dark: "#0d47a1", light: "#e3f2fd", bubble: "#bbdefb" },
    farmer: { name: "Rajesh Kumar", village: "Nashik", crop: "Grapes" },
    daily: "Visit your field this morning. Check the lower leaves carefully — pests usually appear there first.",
    tapLabel: "Tap to speak 👇",
    speakingLabel: "● Speaking...",
    thinkingLabel: "⏳ Getting advice...",
    listenLabel: "🔊 Listen",
    todayLabel: "🌅 Today's Action",
    rainLabel: "Rain",
    questions: [
      "Should I water today?",
      "When to apply fertilizer?",
      "Leaves turning yellow",
      "Should I spray pesticide?",
      "When is harvest time?",
    ],
    responses: [
      "Don't irrigate today. 70% chance of rain in 24 hours. Watering now risks root rot in your crop.",
      "Apply urea after rain stops. Fertilizer washes away in wet soil and wastes your money.",
      "Yellow leaves indicate nitrogen deficiency. Apply 10kg urea per acre. You'll see improvement in 5 days.",
      "Don't spray today — wind is too strong. Spray tomorrow morning before 7am for best results.",
      "Wait 15-20 more days. Stop watering now so grains fill well and you get better yield.",
    ],
    photoResp: "Leaf blight disease detected on your crop. Spray Mancozeb tomorrow morning. Mix 2g per litre of water.",
  },
};

// ── Single Phone Instance ──────────────────────────────────
function PhoneApp({ langCode }) {
  const L = LANGS[langCode];
  const { theme, farmer } = L;

  const [isRecording, setIsRecording] = useState(false);
  const [isThinking, setIsThinking]   = useState(false);
  const [conversation, setConversation] = useState([]);
  const [currentQ, setCurrentQ]       = useState(null);
  const [pulse, setPulse]             = useState(false);
  const [showDaily, setShowDaily]     = useState(true);
  const qIdx    = useRef(0);
  const timer   = useRef(null);
  const chatEnd = useRef(null);

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation]);

  useEffect(() => {
    let t;
    if (isRecording) t = setInterval(() => setPulse(p => !p), 500);
    return () => clearInterval(t);
  }, [isRecording]);

  function handleMic() {
    if (isThinking) return;
    if (isRecording) {
      process();
    } else {
      setIsRecording(true);
      timer.current = setTimeout(process, 4000);
    }
  }

  function process() {
    clearTimeout(timer.current);
    setIsRecording(false);
    const q = L.questions[qIdx.current % L.questions.length];
    const a = L.responses[qIdx.current % L.responses.length];
    qIdx.current++;
    setCurrentQ(q);
    setIsThinking(true);
    setTimeout(() => {
      setConversation(prev => [...prev, {
        q, a,
        time: new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }),
      }]);
      setCurrentQ(null);
      setIsThinking(false);
    }, 1800);
  }

  function handlePhoto() {
    setConversation(prev => [...prev, {
      q: "📸 Photo",
      a: L.photoResp,
      time: new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }),
    }]);
  }

  return (
    <div style={{
      width: 260, height: 540,
      background: "#f8f9fa",
      borderRadius: 28,
      boxShadow: `0 20px 60px rgba(0,0,0,0.2), 0 0 0 2px ${theme.primary}33`,
      display: "flex", flexDirection: "column", overflow: "hidden",
      fontFamily: L.font,
      position: "relative",
    }}>

      {/* Status */}
      <div style={{
        background: theme.dark, padding: "5px 14px",
        display: "flex", justifyContent: "space-between",
      }}>
        <span style={{ color: "rgba(255,255,255,0.7)", fontSize: 10 }}>9:41</span>
        <span style={{ color: "rgba(255,255,255,0.7)", fontSize: 10 }}>📶 🔋</span>
      </div>

      {/* Header */}
      <div style={{
        background: `linear-gradient(135deg, ${theme.dark}, ${theme.primary})`,
        padding: "10px 12px",
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div style={{ fontSize: 13, fontWeight: 800, color: "#fff" }}>🌾 Kisan Saathi</div>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.65)", marginTop: 2 }}>
              {farmer.village} · {farmer.crop}
            </div>
          </div>
          <div style={{
            background: "rgba(255,255,255,0.15)", color: "white",
            fontSize: 9, padding: "4px 8px", borderRadius: 12, fontWeight: 700,
          }}>
            {L.flag} {L.name}
          </div>
        </div>

        {/* Farmer pill */}
        <div style={{
          marginTop: 8, background: "rgba(255,255,255,0.12)",
          borderRadius: 10, padding: "6px 10px",
          display: "flex", alignItems: "center", gap: 8,
        }}>
          <div style={{
            width: 28, height: 28, borderRadius: "50%",
            background: "rgba(255,255,255,0.25)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 14,
          }}>👨‍🌾</div>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, color: "white" }}>{farmer.name}</div>
            <div style={{ fontSize: 9, color: "rgba(255,255,255,0.65)" }}>{L.state}</div>
          </div>
          <div style={{
            marginLeft: "auto", background: "rgba(255,255,255,0.2)",
            padding: "3px 8px", borderRadius: 8,
            fontSize: 9, color: "white", fontWeight: 600,
          }}>
            ☁️ 32°C · 65% {L.rainLabel}
          </div>
        </div>
      </div>

      {/* Chat area */}
      <div style={{ flex: 1, overflowY: "auto", padding: "10px 10px 4px" }}>

        {/* Daily advice */}
        {showDaily && (
          <div style={{
            background: `linear-gradient(135deg, ${theme.dark}, ${theme.primary})`,
            borderRadius: 12, padding: 10, marginBottom: 10, color: "white",
            position: "relative",
          }}>
            <button onClick={() => setShowDaily(false)} style={{
              position: "absolute", top: 6, right: 8,
              background: "rgba(255,255,255,0.2)", border: "none",
              color: "white", borderRadius: "50%", width: 16, height: 16,
              fontSize: 9, cursor: "pointer", lineHeight: "16px", padding: 0,
            }}>✕</button>
            <div style={{ fontSize: 9, opacity: 0.75, marginBottom: 4, fontWeight: 700 }}>
              {L.todayLabel}
            </div>
            <div style={{ fontSize: 11, fontWeight: 600, lineHeight: 1.5 }}>
              {L.daily}
            </div>
            <button style={{
              marginTop: 6, background: "rgba(255,255,255,0.2)",
              border: "none", color: "white", padding: "4px 10px",
              borderRadius: 12, fontSize: 10, cursor: "pointer",
              fontFamily: L.font, fontWeight: 700,
            }}>{L.listenLabel}</button>
          </div>
        )}

        {/* Messages */}
        {conversation.map((c, i) => (
          <div key={i} style={{ marginBottom: 10 }}>
            <div style={{
              background: "white", borderRadius: "10px 10px 10px 2px",
              padding: "8px 10px", maxWidth: "82%",
              boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
            }}>
              <div style={{ fontSize: 9, color: "#bbb", marginBottom: 2 }}>🎤 {c.time}</div>
              <div style={{ fontSize: 12, color: "#333" }}>{c.q}</div>
            </div>
            <div style={{
              background: theme.bubble,
              border: `1px solid ${theme.primary}22`,
              borderRadius: "10px 10px 2px 10px",
              padding: "8px 10px", marginLeft: "auto", maxWidth: "90%",
              marginTop: 5,
            }}>
              <div style={{ fontSize: 12, fontWeight: 600, lineHeight: 1.5, color: "#1a1a1a" }}>
                {c.a}
              </div>
              <button style={{
                marginTop: 5, background: theme.primary, border: "none",
                color: "white", padding: "3px 8px", borderRadius: 10,
                fontSize: 9, cursor: "pointer", fontFamily: L.font, fontWeight: 700,
              }}>{L.listenLabel}</button>
            </div>
          </div>
        ))}

        {/* Thinking */}
        {isThinking && (
          <div style={{ marginBottom: 10 }}>
            <div style={{
              background: "white", borderRadius: "10px 10px 10px 2px",
              padding: "8px 10px", maxWidth: "82%",
            }}>
              <div style={{ fontSize: 12, color: "#333" }}>🎤 {currentQ}</div>
            </div>
            <div style={{
              background: theme.bubble, borderRadius: "10px 10px 2px 10px",
              padding: "10px", marginLeft: "auto", maxWidth: "55%", marginTop: 5,
              display: "flex", alignItems: "center", gap: 6,
            }}>
              <ThinkingDots color={theme.primary} />
            </div>
          </div>
        )}
        <div ref={chatEnd} />
      </div>

      {/* Bottom bar */}
      <div style={{
        background: "white", borderTop: "1px solid #eee",
        padding: "8px 12px 10px",
      }}>
        <div style={{ textAlign: "center", marginBottom: 8, height: 14 }}>
          <span style={{
            fontSize: 10, fontWeight: 600,
            color: isRecording ? "#c62828" : isThinking ? theme.primary : "#aaa",
          }}>
            {isRecording ? L.speakingLabel : isThinking ? L.thinkingLabel : L.tapLabel}
          </span>
        </div>

        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 14 }}>
          {/* Camera */}
          <button onClick={handlePhoto} style={{
            width: 38, height: 38, borderRadius: "50%",
            background: "#f5f5f5", border: "2px solid #e8e8e8",
            fontSize: 16, cursor: "pointer",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>📸</button>

          {/* MIC */}
          <button
            onClick={handleMic}
            disabled={isThinking}
            style={{
              width: 58, height: 58, borderRadius: "50%", border: "none",
              fontSize: 22, cursor: isThinking ? "not-allowed" : "pointer",
              color: "white",
              background: isRecording ? "#c62828" : isThinking ? "#bbb" : theme.primary,
              boxShadow: isRecording
                ? "0 0 0 8px rgba(198,40,40,0.15)"
                : `0 4px 16px ${theme.primary}55`,
              transform: isRecording && pulse ? "scale(1.1)" : "scale(1)",
              transition: "all 0.2s",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
            {isThinking ? "⏳" : isRecording ? "⏹" : "🎤"}
          </button>

          {/* Clear */}
          <button onClick={() => { setConversation([]); setShowDaily(true); }} style={{
            width: 38, height: 38, borderRadius: "50%",
            background: "#f5f5f5", border: "2px solid #e8e8e8",
            fontSize: 16, cursor: "pointer",
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
    const t = setInterval(() => setDot(d => (d + 1) % 3), 380);
    return () => clearInterval(t);
  }, []);
  return (
    <div style={{ display: "flex", gap: 5, padding: "2px 0" }}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          width: 8, height: 8, borderRadius: "50%",
          background: i === dot ? color : "#ddd",
          transition: "background 0.2s",
        }} />
      ))}
    </div>
  );
}

// ── Root: Three phones side by side ───────────────────────
export default function ThreePhones() {
  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      padding: "20px 10px",
      fontFamily: "sans-serif",
    }}>
      {/* Title */}
      <div style={{ textAlign: "center", marginBottom: 28 }}>
        <div style={{ fontSize: 32, marginBottom: 6 }}>🌾</div>
        <div style={{ fontSize: 22, fontWeight: 800, color: "white", letterSpacing: 1 }}>
          Kisan Saathi
        </div>
        <div style={{ fontSize: 13, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>
          One app · Three languages · Millions of farmers
        </div>
      </div>

      {/* Language labels */}
      <div style={{ display: "flex", gap: 20, marginBottom: 16 }}>
        {[
          { flag: "🟠", label: "Maharashtra", sub: "मराठी" },
          { flag: "🔴", label: "Tamil Nadu",  sub: "தமிழ்" },
          { flag: "🔵", label: "All India",   sub: "English" },
        ].map(l => (
          <div key={l.label} style={{
            width: 260, textAlign: "center",
          }}>
            <div style={{ fontSize: 16, color: "white", fontWeight: 700 }}>
              {l.flag} {l.label}
            </div>
            <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)" }}>{l.sub}</div>
          </div>
        ))}
      </div>

      {/* Three phones */}
      <div style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
        <PhoneApp langCode="mr" />
        <PhoneApp langCode="ta" />
        <PhoneApp langCode="en" />
      </div>

      {/* Footer */}
      <div style={{ marginTop: 24, textAlign: "center" }}>
        <div style={{ fontSize: 12, color: "rgba(255,255,255,0.35)" }}>
          Press 🎤 on each phone · Each responds in its own language
        </div>
        <div style={{ fontSize: 11, color: "rgba(255,255,255,0.2)", marginTop: 4 }}>
          Built with Claude · Anthropic
        </div>
      </div>
    </div>
  );
}
