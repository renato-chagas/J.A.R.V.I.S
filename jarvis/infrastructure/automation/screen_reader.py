import mss
import mss.tools
import os
import logging
import subprocess
try:
    import pytesseract
    from PIL import Image, ImageOps, ImageFilter, ImageEnhance
except Exception:
    pytesseract = None
    Image = None
    ImageOps = None
    ImageEnhance = None

class ScreenReader:
    """Radar visual: Captura a tela para análise do agente."""
    
    def __init__(self):
        self.sct = mss.mss()
        # Define o caminho para salvar os prints temporários dentro da sua estrutura de dados
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_dir = os.path.abspath(os.path.join(base_dir, "../../../data/temp_screen"))
        
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        
        # Detectar Wayland vs X11
        self.is_wayland = os.getenv('XDG_SESSION_TYPE', '').lower() == 'wayland'
        logging.info(f"Sistema: {'Wayland' if self.is_wayland else 'X11'}")

    def _capture_grim(self, output_filename: str) -> bool:
        """Tenta capturar com grim (Wayland)."""
        try:
            subprocess.run(['grim', output_filename], check=True, capture_output=True, timeout=5)
            logging.info(f"Captura grim sucesso.")
            return True
        except Exception as e:
            logging.debug(f"grim falhou: {e}")
            return False

    def _capture_scrot(self, output_filename: str) -> bool:
        """Tenta capturar com scrot (X11/fallback)."""
        try:
            subprocess.run(['scrot', output_filename], check=True, capture_output=True, timeout=5)
            logging.info(f"Captura scrot sucesso.")
            return True
        except Exception as e:
            logging.debug(f"scrot falhou: {e}")
            return False

    def _é_imagem_vazia(self, img_path: str) -> bool:
        """Verifica se a imagem capturada é principalmente preta/vazia."""
        if not os.path.exists(img_path):
            return True
        try:
            img = Image.open(img_path)
            # Converter para grayscale e calcular média de brilho
            gray = img.convert('L')
            pixels = list(gray.getdata())
            media_brilho = sum(pixels) / len(pixels)
            # Se média < 30 (escala 0-255), imagem está muito escura
            return media_brilho < 30
        except Exception:
            return False

    def capture_monitors(self, monitor_id: int = 1):
        """Captura um monitor específico (1 ou 2)."""
        # mss.monitors retorna: [tudo, mon1, mon2, ...]
        # Ajustamos para evitar erro de índice
        if monitor_id >= len(self.sct.monitors):
            logging.warning(f"Monitor {monitor_id} não detectado. Usando monitor 1.")
            monitor_id = 1
            
        output_filename = os.path.join(self.temp_dir, f"monitor_{monitor_id}.png")
        try:
            logging.info(f"Capturando monitor {monitor_id}.")
            # Captura a área do monitor solicitado
            self.sct.shot(mon=monitor_id, output=output_filename)
            logging.info(f"Monitor {monitor_id} capturado.")
            return output_filename
        except Exception as e:
            logging.error(f"Erro ao capturar monitor {monitor_id}: {e}")
            return None

    def capture_full_desktop(self):
        """Captura o desktop completo (ambos os monitores)."""
        output_filename = os.path.join(self.temp_dir, "full_desktop.png")
        try:
            logging.info("Capturando desktop completo.")
            
            # Em Wayland, tentar grim primeiro
            if self.is_wayland:
                if self._capture_grim(output_filename):
                    return output_filename
            
            # Fallback: tentar scrot
            if self._capture_scrot(output_filename):
                return output_filename
            
            # Último recurso: mss
            logging.info("Tentando captura com mss.")
            self.sct.shot(output=output_filename)
            logging.info("Desktop completo capturado.")
            return output_filename
        except Exception as e:
            logging.error(f"Erro ao capturar desktop completo: {e}")
            return None
        
    def limpar_print(self, file_path: str):
        """Exclui o arquivo de print após o uso."""
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logging.info(f"Removido arquivo temporário.")
            except Exception as e:
                logging.error(f"Erro ao remover arquivo temporário: {e}")

    def capturar_tudo(self):
        """Alias em português para capturar o desktop completo."""
        return self.capture_full_desktop()

    def _ocr_avancado(self, img_path: str) -> str:
        """Tenta extrair texto com múltiplas técnicas de preprocessing.
        
        Retorna o texto extraído (string vazia se falhar em todas as tentativas).
        """
        if not os.path.exists(img_path):
            return ""
        
        melhor_texto = ""
        
        # Estratégia 1: OCR direto (menos processamento, mais rápido)
        try:
            img = Image.open(img_path)
            try:
                txt = pytesseract.image_to_string(img, lang="por+eng")
            except Exception:
                txt = pytesseract.image_to_string(img)
            txt = txt.strip()
            if len(txt) > len(melhor_texto):
                melhor_texto = txt
                logging.info(f"Estratégia 1 (direto): {len(txt)} chars")
        except Exception as e:
            logging.debug(f"Estratégia 1 falhou: {e}")
        
        # Estratégia 2: Grayscale + Contrast
        try:
            img = Image.open(img_path).convert('L')
            img = ImageOps.autocontrast(img)
            try:
                txt = pytesseract.image_to_string(img, lang="por+eng")
            except Exception:
                txt = pytesseract.image_to_string(img)
            txt = txt.strip()
            if len(txt) > len(melhor_texto):
                melhor_texto = txt
                logging.info(f"Estratégia 2 (grayscale+contrast): {len(txt)} chars")
        except Exception as e:
            logging.debug(f"Estratégia 2 falhou: {e}")
        
        # Estratégia 3: Binarização com threshold
        try:
            img = Image.open(img_path).convert('L')
            img = img.point(lambda x: 0 if x < 140 else 255, '1')
            try:
                txt = pytesseract.image_to_string(img, lang="por+eng")
            except Exception:
                txt = pytesseract.image_to_string(img)
            txt = txt.strip()
            if len(txt) > len(melhor_texto):
                melhor_texto = txt
                logging.info(f"Estratégia 3 (binarizado): {len(txt)} chars")
        except Exception as e:
            logging.debug(f"Estratégia 3 falhou: {e}")
        
        # Estratégia 4: Upscale 2x + Contrast
        try:
            img = Image.open(img_path).convert('L')
            w, h = img.size
            img = img.resize((w*2, h*2), Image.BICUBIC)
            img = ImageOps.autocontrast(img)
            try:
                txt = pytesseract.image_to_string(img, lang="por+eng")
            except Exception:
                txt = pytesseract.image_to_string(img)
            txt = txt.strip()
            if len(txt) > len(melhor_texto):
                melhor_texto = txt
                logging.info(f"Estratégia 4 (upscale 2x+contrast): {len(txt)} chars")
        except Exception as e:
            logging.debug(f"Estratégia 4 falhou: {e}")
        
        # Estratégia 5: Sharpening
        try:
            img = Image.open(img_path)
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(2.0)
            try:
                txt = pytesseract.image_to_string(img, lang="por+eng")
            except Exception:
                txt = pytesseract.image_to_string(img)
            txt = txt.strip()
            if len(txt) > len(melhor_texto):
                melhor_texto = txt
                logging.info(f"Estratégia 5 (sharpening): {len(txt)} chars")
        except Exception as e:
            logging.debug(f"Estratégia 5 falhou: {e}")
        
        return melhor_texto

    def capturar_e_ler(self, monitor_id: int = 2) -> str:
        """Captura o monitor especificado e extrai texto via Tesseract OCR.

        Retorna o texto extraído (string vazia se nada ou em caso de erro).
        Se o monitor solicitado estiver vazio/preto, tenta fallback.
        """
        if pytesseract is None or Image is None:
            logging.error("OCR não disponível: instale pytesseract e Pillow.")
            return ""

        # Tentar monitor solicitado
        caminho = self.capture_monitors(monitor_id)
        if caminho and self._é_imagem_vazia(caminho):
            logging.info(f"Monitor {monitor_id} está vazio/preto — tentando fallback.")
            self.limpar_print(caminho)
            # Fallback 1: Tentar monitor 1
            caminho = self.capture_monitors(1)
            if caminho and self._é_imagem_vazia(caminho):
                logging.info("Monitor 1 também está vazio — tentando desktop agregado.")
                self.limpar_print(caminho)
                # Fallback 2: Desktop agregado (todos os monitores)
                caminho = self.capture_full_desktop()

        if not caminho:
            return ""

        texto = ""
        try:
            logging.info(f"Processando OCR.")
            texto = self._ocr_avancado(caminho)
            logging.info(f"OCR concluído: {len(texto)} caracteres.")
            return texto
        except Exception as e:
            logging.error(f"Erro OCR: {e}")
            return ""
        finally:
            try:
                if texto:
                    # Resultado presente: removemos o arquivo temporário
                    self.limpar_print(caminho)
                else:
                    # Sem texto: preservamos a imagem para depuração e renomeamos
                    failed_name = os.path.join(self.temp_dir, f"failed_capture.png")
                    try:
                        os.replace(caminho, failed_name)
                        logging.info(f"Imagem preservada: {failed_name}")
                    except Exception:
                        # Se não conseguiu renomear, tente remover silenciosamente
                        try:
                            self.limpar_print(caminho)
                        except Exception:
                            pass
            except Exception:
                pass

    def capturar_full_e_ler(self) -> str:
        """Captura o desktop completo e extrai texto via Tesseract OCR."""
        if pytesseract is None or Image is None:
            logging.error("OCR não disponível: instale pytesseract e Pillow.")
            return ""

        caminho = self.capture_full_desktop()
        if not caminho:
            return ""

        texto = ""
        try:
            logging.info("Processando OCR do desktop completo.")
            texto = self._ocr_avancado(caminho)
            logging.info(f"OCR desktop concluído: {len(texto)} caracteres.")
            return texto
        except Exception as e:
            logging.error(f"Erro OCR desktop: {e}")
            return ""
        finally:
            try:
                if texto:
                    self.limpar_print(caminho)
                else:
                    failed_name = os.path.join(self.temp_dir, "failed_full.png")
                    try:
                        os.replace(caminho, failed_name)
                        logging.info(f"Imagem preservada: {failed_name}")
                    except Exception:
                        try:
                            self.limpar_print(caminho)
                        except Exception:
                            pass
            except Exception:
                pass