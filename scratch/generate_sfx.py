import numpy as np
import wave
import os

SAMPLE_RATE = 48000
OUT_DIR = os.path.join('promo', 'public', 'audio')
os.makedirs(OUT_DIR, exist_ok=True)

def write_wav(filename, samples):
    # Ensure float32 normalized to [-1, 1]
    samples = np.clip(samples, -0.98, 0.98)
    int_samples = (samples * 32767).astype(np.int16)
    path = os.path.join(OUT_DIR, filename)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(int_samples.tobytes())
    print(f"Generated {filename}: {len(samples)/SAMPLE_RATE:.3f}s ({os.path.getsize(path)} bytes)")

# 1. Haptic Tap (crisp, subtle mobile UI click)
def gen_tap():
    dur = 0.025
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), False)
    freq = 1200 * np.exp(-t * 120)
    sig = np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.004)
    # Add subtle high-frequency transient click
    transient = np.random.uniform(-0.3, 0.3, len(t)) * np.exp(-t / 0.001)
    return sig * 0.7 + transient * 0.3

# 2. Card Lift (tactile elevation)
def gen_card_lift():
    dur = 0.16
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), False)
    freq = 180 + 160 * (1 - np.exp(-t * 25))
    sig = np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.04)
    noise = np.random.normal(0, 0.15, len(t)) * np.exp(-t / 0.02)
    return sig * 0.6 + noise

# 3. Whoosh Enter (phone fly-in from below)
def gen_whoosh_enter():
    dur = 0.75
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), False)
    noise = np.random.normal(0, 1, len(t))
    # Filter envelope using bell curve
    env = np.sin(np.pi * t / dur) ** 2.2
    # Moving frequency modulation (pseudo bandpass)
    carrier = np.sin(2 * np.pi * (160 + 400 * np.sin(np.pi * t / dur)) * t)
    sig = (noise * 0.35 + carrier * 0.65) * env
    return sig * 0.5

# 4. Error Shake (wrong answer impact + dissonant beat)
def gen_error_shake():
    dur = 0.55
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), False)
    sub = np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.12)
    # Dissonant acoustic beating (148Hz & 156Hz -> 8Hz flutter)
    dissonance = (np.sin(2 * np.pi * 148 * t) + np.sin(2 * np.pi * 156 * t)) * np.exp(-t / 0.18) * 0.5
    thud = np.random.normal(0, 0.3, len(t)) * np.exp(-t / 0.03)
    sig = sub * 0.6 + dissonance * 0.4 + thud * 0.3
    return sig * 0.75

# 5. Slide (smooth lateral transition)
def gen_slide():
    dur = 0.32
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), False)
    env = np.sin(np.pi * t / dur) ** 1.8
    noise = np.random.normal(0, 0.4, len(t))
    sweep = np.sin(2 * np.pi * (300 + 500 * np.sin(np.pi * t / dur)) * t)
    return (noise * 0.3 + sweep * 0.7) * env * 0.45

# 6. Drawer Open (bottom sheet slide up)
def gen_drawer_open():
    dur = 0.28
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), False)
    freq = 240 + 380 * (t / dur)
    env = np.sin(np.pi * t / dur) ** 1.6
    sig = np.sin(2 * np.pi * freq * t) * env
    return sig * 0.5

# 7. Typing (rapid subtle key clicks)
def gen_typing():
    dur = 0.35
    total_len = int(SAMPLE_RATE * dur)
    sig = np.zeros(total_len)
    click_times = [0.02, 0.08, 0.14, 0.21, 0.27, 0.32]
    for ct in click_times:
        idx = int(ct * SAMPLE_RATE)
        c_dur = 0.012
        c_t = np.linspace(0, c_dur, int(SAMPLE_RATE * c_dur), False)
        f0 = np.random.uniform(2200, 3200)
        c_sig = np.sin(2 * np.pi * f0 * c_t) * np.exp(-c_t / 0.002)
        end = min(idx + len(c_sig), total_len)
        sig[idx:end] += c_sig[:end - idx] * 0.35
    return sig

# 8. AI Stream (crystal synth shimmer)
def gen_ai_stream():
    dur = 0.65
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), False)
    # E6 (1318.5 Hz), G#6 (1661.2 Hz), B6 (1975.5 Hz)
    f1, f2, f3 = 1318.5, 1661.2, 1975.5
    s1 = np.sin(2 * np.pi * f1 * t) * np.exp(-t / 0.28)
    s2 = np.sin(2 * np.pi * f2 * t) * np.exp(-t / 0.24)
    s3 = np.sin(2 * np.pi * f3 * t) * np.exp(-t / 0.20)
    # Soft shimmer / chorus
    shimmer = np.sin(2 * np.pi * 6 * t) * 0.1
    sig = (s1 * 0.4 + s2 * 0.35 + s3 * 0.25) * (1 + shimmer)
    return sig * 0.55

# 9. Whip Pan
def gen_whip():
    dur = 0.24
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), False)
    env = np.sin(np.pi * t / dur) ** 2.5
    noise = np.random.normal(0, 0.8, len(t)) * env
    sweep = np.sin(2 * np.pi * (400 + 800 * (t / dur)) * t) * env
    return (noise * 0.5 + sweep * 0.5) * 0.5

# 10. Success Celebration (Nailed it! major chime + confetti sparkle)
def gen_success():
    dur = 0.95
    total_len = int(SAMPLE_RATE * dur)
    sig = np.zeros(total_len)
    # Pentatonic bell sequence: C6, E6, G6, C7
    notes = [1046.5, 1318.5, 1567.98, 2093.0]
    stagger = [0.0, 0.035, 0.075, 0.12]
    for freq, st in zip(notes, stagger):
        idx = int(st * SAMPLE_RATE)
        rem = total_len - idx
        t_note = np.linspace(0, rem / SAMPLE_RATE, rem, False)
        # Add fundamental + octave overtone
        bell = (np.sin(2 * np.pi * freq * t_note) * 0.7 + 
                np.sin(2 * np.pi * freq * 2 * t_note) * 0.3) * np.exp(-t_note / 0.35)
        sig[idx:] += bell * 0.28
    # Confetti soft flutter / sparkle
    t = np.linspace(0, dur, total_len, False)
    sparkle = np.random.normal(0, 0.15, total_len) * np.exp(-t / 0.18) * np.sin(2 * np.pi * 3200 * t)
    sig += sparkle * 0.25
    return sig * 0.85

# 11. Score Count-Up Ticker
def gen_counter():
    dur = 1.15
    total_len = int(SAMPLE_RATE * dur)
    sig = np.zeros(total_len)
    num_ticks = 24
    for i in range(num_ticks):
        # Progressively accelerate tick intervals
        p = i / (num_ticks - 1)
        tick_time = 0.05 + 1.0 * (p ** 1.1)
        idx = int(tick_time * SAMPLE_RATE)
        if idx >= total_len:
            break
        # Rising pitch from 900Hz to 1750Hz
        freq = 900 + 850 * p
        t_len = int(SAMPLE_RATE * 0.015)
        t_tick = np.linspace(0, 0.015, t_len, False)
        tick = np.sin(2 * np.pi * freq * t_tick) * np.exp(-t_tick / 0.003)
        end = min(idx + t_len, total_len)
        sig[idx:end] += tick[:end - idx] * (0.25 + 0.15 * p)
    # Final confirmation chime at 1.05s
    idx_final = int(1.05 * SAMPLE_RATE)
    rem = total_len - idx_final
    t_fin = np.linspace(0, rem / SAMPLE_RATE, rem, False)
    chime = (np.sin(2 * np.pi * 1760 * t_fin) * 0.7 + np.sin(2 * np.pi * 2637 * t_fin) * 0.3) * np.exp(-t_fin / 0.15)
    sig[idx_final:] += chime * 0.4
    return sig * 0.8

# 12. Chip Pop
def gen_chip_pop():
    dur = 0.09
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), False)
    freq = 380 + 440 * (t / dur)
    sig = np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.018)
    return sig * 0.55

# 13. Outro Reveal (warm harmonic chord + sub impact)
def gen_outro():
    dur = 1.9
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), False)
    # Warm sub impact at 75Hz
    sub = np.sin(2 * np.pi * 75 * t) * np.exp(-t / 0.25) * 0.5
    # Major 9th chord: D4 (293.66), F#4 (369.99), A4 (440.0), C#5 (554.37), E5 (659.25)
    chord = (
        np.sin(2 * np.pi * 293.66 * t) * 0.35 +
        np.sin(2 * np.pi * 369.99 * t) * 0.25 +
        np.sin(2 * np.pi * 440.00 * t) * 0.20 +
        np.sin(2 * np.pi * 554.37 * t) * 0.15 +
        np.sin(2 * np.pi * 659.25 * t) * 0.12
    ) * np.exp(-t / 0.65)
    sig = sub + chord
    return sig * 0.75

write_wav('sfx_tap.wav', gen_tap())
write_wav('sfx_card_lift.wav', gen_card_lift())
write_wav('sfx_whoosh_enter.wav', gen_whoosh_enter())
write_wav('sfx_error_shake.wav', gen_error_shake())
write_wav('sfx_slide.wav', gen_slide())
write_wav('sfx_drawer_open.wav', gen_drawer_open())
write_wav('sfx_typing.wav', gen_typing())
write_wav('sfx_ai_stream.wav', gen_ai_stream())
write_wav('sfx_whip.wav', gen_whip())
write_wav('sfx_success.wav', gen_success())
write_wav('sfx_counter.wav', gen_counter())
write_wav('sfx_chip_pop.wav', gen_chip_pop())
write_wav('sfx_outro.wav', gen_outro())
print("ALL SFX GENERATED SUCCESSFULLY!")
