# Mediapipe Kullanarak El Hareketleriyle X-Plane Uçuş Kontrolü
For English explanation, please refer to the [**English README**](./README_english.md).

Bu proje, **Mediapipe** kullanarak el hareketlerinden anlam çıkarıp, **X-Plane 11** uçuş simülatörünü gerçek zamanlı olarak kontrol etmeyi amaçlamaktadır. Sağ el throttle ve uçuş başlatma için, sol el ise pitch ve roll kontrolü için kullanılır.

## Kullanılan Kütüphaneler

* `cv2` – Görüntü işleme için OpenCV
* `mediapipe` – El pozisyonu tespiti için
* `xpc` – X-Plane uçuş kontrolü için Python Client

## Sistem Mimarisi

### Genel Akış

1. Mediapipe ile her iki elin 21 landmark (eklem) noktası alınır.
2. Bu landmark'lar her karede `(x, y)` koordinatına çevrilip bir `dict` yapısında saklanır:
3. Sağ el için yumruk algılanarak uçuş başlatılır.
4. Sağ elin orta parmağı ile bilek arasındaki mesafe kullanılarak throttle değeri hesaplanır.
5. Sol elin orta parmak boğumunun pozisyonu ile pitch ve roll hesaplanır.
6. Elde edilen kontrol girdileri X-Plane’e aktarılır.

---

## 1. Yumruk (Fist) Algılama

Sağ eldeki orta parmağın ucu ile bilek mesafesi,
orta parmağın alt boğum noktası ile bilek mesafesinden küçükse yumruk yapılmış sayılır.

```python
def Fist(fingers):

    if fingers != None:
        sum_top = 0
      
        x_error = abs(fingers["middle_top"][0][0] - fingers["wrist"][0][0])
        y_error = abs(fingers["middle_top"][0][1] - fingers["wrist"][0][1])

        sum_top += ((x_error**2 + y_error**2)**(0.5))

        sum_bottom = 0

        x_error = abs(fingers["middle_bottom"][0][0] - fingers["wrist"][0][0])
        y_error = abs(fingers["middle_bottom"][0][1] - fingers["wrist"][0][1])

        sum_bottom += ((x_error**2 + y_error**2)**(0.5))

        if sum_bottom > sum_top:
            return "Close"
        else:
            return "Open"
    else:
       return None
```

![Yumruk Gösterimi](readme_images/Fist.png)

---

## 2. Throttle (Gaz) Hesaplama

Sağ el açık konumdayken, orta parmak ucu ile orta boğum arasındaki mesafe ölçülür. Bu mesafe, orta boğum ile bilek arasındaki mesafeye bölünerek normalize edilir. Ortaya çıkan oran throttle (gaz seviyesi) olarak kullanılır.
Bu yöntemle parmak açıldıkça throttle artar, kapandıkça azalır.

```python
def ThrottleRange(image , fingers):

    if fingers != None:
        y_error = abs(fingers["middle_top"][0][1] - fingers["middle_bottom"][0][1])
        x_error = abs(fingers["middle_top"][0][0] - fingers["middle_bottom"][0][0])

        error1 = ((x_error**2 + y_error**2)**(0.5))

        y_error1 = abs(fingers["middle_bottom"][0][1] - fingers["wrist"][0][1])
        x_error1 = abs(fingers["middle_bottom"][0][0] - fingers["wrist"][0][0])

        error2 = ((x_error1**2 + y_error1**2)**(0.5)) - 50

        throttle = error1 / error2
        cv2.putText(image, f"Throttle : {throttle:.2f}", (fingers["middle_bottom"][0][0] - 50, fingers["middle_bottom"][0][1] + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        return throttle
    else:
       return None
```

![Sağ el açık – throttle seviyesi gösterimi](readme_images/Throttle.png)

---

## 3. Pitch ve Roll Hesaplama

Sol elin orta parmak alt boğumu (landmark 9) referans alınır. Bu nokta, ekranın sol çeyrek merkezine göre konumlandırılır. Yani ekranın sol kısmında belirlenen bir sanal merkez noktaya göre hareket ettikçe:

Yukarı/aşağı hareketi pitch (eğim)

Sağa/sola hareketi roll (yana yatış)

olarak değerlendirilir. Bu farklar ölçeklenerek X-Plane'e gönderilen kontrol girdilerine dönüştürülür.

```python
def Pitch_roll(fingers):

   pitch_roll_x = width // 4
   pitch_roll_y = height // 2 

   if fingers != None:
      cv2.circle(image,(int(fingers["middle_bottom"][0][0]),int(fingers["middle_bottom"][0][1])),30,(255,0,0),3)
      
      roll = pitch_roll_x - fingers["middle_bottom"][0][0] 
      pitch = pitch_roll_y - fingers["middle_bottom"][0][1]

   else:
        return None ,None

   return roll ,pitch
```

![GÖRSEL: Sol el orta parmak hareketiyle pitch–roll kontrolü](readme_images/Pitch_Roll.png)

---

## 4. Hesaplanan Değerlerin X-Plane 11 'e gönderilmesi
Elde edilen Pitch, Roll, Throttle değerleri, xpc (X-Plane Connect) kütüphanesi aracılığıyla X-Plane 11'e gönderilerek uçağın kontrol yüzeyleri gerçek zamanlı olarak kontrol edilir.

```python
controller.send_controls(
            elevator = -1*(Roll / 250) , 
            aileron = -1*(Pitch / 300),
            throttle = Throttle , 
            rudder = 0
            )
```

## 5. Landmark Dönüşümü

![Sağ el açık – throttle seviyesi gösterimi](readme_images/Landmark.PNG)

Mediapipe, her el için indexlenmiş olarak 21 adet landmark verir. Bunlar `(x, y)` olarak alınır ve `dict` içinde saklanır:

```python
def FingerPoints(hand):

    hand_index = hand.multi_hand_landmarks
    hands = {"right":None,"left":None}
    
    for idx , hand_landmarks in enumerate(hand_index):
        
        try:
          fingers = {
                      "index_top": [None,8],
                      "index_bottom": [None,5],
                      "middle_top": [None,12],
                      "middle_bottom": [None,9],
                      "ring_top": [None,16],
                      "ring_bottom": [None,13],
                      "pinky_top": [None,20],
                      "pinky_bottom": [None,17],
                      "wrist" : [None,0]
                      }
          
          for point in fingers.keys():
             num = fingers[point][1]
             landmark = (results.multi_hand_landmarks[idx].landmark[num].x,results.multi_hand_landmarks[idx].landmark[num].y)
             landmark_xy = int(width * landmark[0]) , int(height * landmark[1])
             fingers[point][0] = landmark_xy

          if hand.multi_handedness[idx].classification[0].label == "Right":
            hands["right"] = fingers
          else:
            hands["left"] = fingers

        except:
          pass
        
    return hands
```

Bu yapı sayesinde her landmark, indeks ile kolayca erişilebilir hale gelir.

---


## Kurulum ve Çalıştırma

### X-Plane 11 Bağlantısı

![X-Plane 11 Data](readme_images/X-Plane_11_Data.png)

X-Plane 11’den telemetri paketlerinin alınabilmesi ve veri gönderilebilmesi için veri akışı aktif edilmelidir.
X-Plane 11 → Ayarlar → Data Output menüsüne giderek Send output data seçeneğini aktif hale getirin.

IP Adresi: 127.0.0.1

Port: 49001

Not: Bu ayarlar sayesinde Mission Planner gibi yer kontrol yazılımlarına da bağlantı sağlayabilirsiniz.

### Gereksinimler

```bash
pip install opencv-python mediapipe
```

### Çalıştırma

```bash
python main.py
```

---

## Örnek Kullanım Videosu ve Görseller

[![Watch the demo](https://img.youtube.com/vi/mk37UO0KcNg/maxresdefault.jpg)](https://youtu.be/mk37UO0KcNg)

---

## Notlar
X-Plane 11 bağlantısı olmadan test etmek için test.py dosyasını kullanabilirsiniz. Ayrıca, projelerinizi geliştirmek için hayal gücünüze bağlı olarak farklı kullanım senaryolarında da uygulayabilirsiniz.


