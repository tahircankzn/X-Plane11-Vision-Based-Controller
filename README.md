
# Hand Gesture Controlled Flight in X-Plane using Mediapipe

Bu proje, **Mediapipe** kullanarak ellerin konumundan ve hareketinden anlam çıkarıp, **X-Plane 11** uçuş simülatörünü kontrol etmeyi amaçlar. Sağ el ile throttle (gaz) kontrolü ve uçuş başlatma yapılırken, sol el ile pitch–roll (yani eğim ve yana yatış) kontrolü sağlanır.

## Kullanılan Kütüphaneler

* `cv2` – Görüntü işleme için OpenCV
* `mediapipe` – El pozisyonu tespiti için
* `math` – Öklidyen mesafe hesaplama
* `xpc` – X-Plane uçuş kontrolü için Python Client


## Sistem Mimarisi

### Genel Akış

1. Mediapipe ile her iki elin 21 landmark (eklem) noktası alınır.
2. Bu landmarklar her karede `(x, y)` koordinatına çevrilip bir `dict` yapısında saklanır:

   ```python
   left_landmarks = {0: (x0, y0), 1: (x1, y1), ..., 20: (x20, y20)}
   right_landmarks = {...}
   ```
3. Sağ el için yumruk algılanarak uçuş başlatılır.
4. Sağ elin orta parmağı ile bilek arasındaki mesafe kullanılarak throttle değeri hesaplanır.
5. Sol elin orta parmak boğumunun pozisyonu ile pitch ve roll hesaplanır.
6. Elde edilen kontrol girdileri X-Plane’e aktarılır.

---

## 1. Yumruk (Fist) Algılama

Sağ eldeki dört parmak (işaret, orta, yüzük, serçe) uçlarının, alt boğumlarına olan mesafesi kontrol edilir. Eğer bu mesafeler bir eşikten küçükse parmak kapalı kabul edilir.

```python
def is_fist(right_landmarks):
    tips = [8, 12, 16, 20]
    lowers = [6, 10, 14, 18]
    for tip, lower in zip(tips, lowers):
        if calculate_distance(right_landmarks[tip], right_landmarks[lower]) > 0.05:
            return False
    return True
```

**\[GÖRSEL: Sağ elde yumruk yapılmış hali]**

---

## 2. Throttle (Gaz) Hesaplama

Sağ el açıkken, orta parmağın ucu ile bilek arasındaki mesafe ölçülerek normalize edilir. Bu değer `throttle` olarak kullanılır.

```python
distance = calculate_distance(right_landmarks[12], right_landmarks[0])
throttle = min(distance * 2.5, 1.0)
```

Bu değer `xpc.Client().sendCTRL()` fonksiyonu ile X-Plane’e aktarılır.

![Sağ el açık – throttle seviyesi gösterimi](readme_images/Throttle.png)

---

## 3. Pitch ve Roll Hesaplama

Sol elin orta parmak alt boğumu (nokta 10), ekran merkezine göre yer değiştirmesiyle `pitch` ve `roll` kontrolü yapılır.

```python
ref_x, ref_y = 0.5, 0.5
curr_x, curr_y = left_landmarks[10]
dx = ref_x - curr_x
dy = ref_y - curr_y

roll = max(min(dx * 2, 1.0), -1.0)
pitch = max(min(dy * 2, 1.0), -1.0)
```

Bu değerler throttle ile birlikte gönderilir:

```python
client.sendCTRL([roll, pitch, throttle, 0])
```

![GÖRSEL: Sol el orta parmak hareketiyle pitch–roll kontrolü](readme_images/Pitch_Roll.png)

---

## 4. Landmark Dönüşümü

Mediapipe, her el için 21 adet landmark verir. Bunlar `(x, y)` olarak alınır ve `dict` içinde saklanır:

```python
for i, lm in enumerate(handLms.landmark):
    cx, cy = int(lm.x * width), int(lm.y * height)
    if hand_label == "Left":
        left_landmarks[i] = (lm.x, lm.y)
    else:
        right_landmarks[i] = (lm.x, lm.y)
```

Bu yapı sayesinde her landmark, indeks ile kolayca erişilebilir hale gelir.

---

## Demo
[![Watch the demo](https://img.youtube.com/vi/mk37UO0KcNg/maxresdefault.jpg)](https://youtu.be/mk37UO0KcNg)

## Kurulum ve Çalıştırma

### Gereksinimler

```bash
pip install opencv-python mediapipe
```

Ayrıca, X-Plane 11’de [XPC Plugin](https://github.com/nasa/XPlaneConnect) kurulmuş ve çalışır durumda olmalıdır.

### Çalıştırma

```bash
python main.py
```

---

## Örnek Kullanım Videosu ve Görseller

**\[Buraya kontrol ekranından alınmış ekran görüntüleri veya videolar eklenecek]**

---

## Notlar

* Pitch–Roll referans noktası ekran merkezidir.
* Sağ el, sadece throttle ve kalkış tetiklemesi içindir.
* Sol el ile uçuş yönü kontrol edilir.

