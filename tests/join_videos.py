"""
Junta os vídeos do PWA e Dashboard em um único arquivo MP4
Usa ffmpeg via subprocess
"""
import subprocess
import os
from pathlib import Path

def join_videos():
    videos_dir = Path(__file__).parent / 'videos'
    
    # Encontrar os vídeos gravados (webm)
    webm_files = sorted(videos_dir.glob('*.webm'))
    
    if len(webm_files) < 2:
        print(f"❌ Precisamos de pelo menos 2 vídeos. Encontrados: {len(webm_files)}")
        print(f"📁 Diretório: {videos_dir}")
        for f in webm_files:
            print(f"   - {f.name}")
        return
    
    # Assume que o primeiro é PWA e o segundo é Dashboard (por ordem de criação)
    pwa_video = webm_files[0]
    dashboard_video = webm_files[1]
    
    print(f"📹 PWA: {pwa_video.name}")
    print(f"📹 Dashboard: {dashboard_video.name}")
    
    # Criar arquivo de concatenação
    concat_file = videos_dir / 'concat.txt'
    with open(concat_file, 'w') as f:
        f.write(f"file '{pwa_video}'\n")
        f.write(f"file '{dashboard_video}'\n")
    
    # Output final
    output_file = videos_dir / 'terrapilot-demo-final.mp4'
    
    print(f"\n🔧 Juntando vídeos com ffmpeg...")
    print(f"📤 Output: {output_file}")
    
    # Comando ffmpeg para concatenar e converter para MP4 H.264
    cmd = [
        'ffmpeg',
        '-y',                           # Sobrescrever sem perguntar
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-c:v', 'libx264',              # Codec H.264 (compatível com YouTube)
        '-preset', 'medium',            # Balance entre velocidade e qualidade
        '-crf', '23',                   # Qualidade (18=alta, 28=baixa)
        '-pix_fmt', 'yuv420p',          # Formato de pixel compatível
        '-movflags', '+faststart',      # Otimizar para streaming
        str(output_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"\n✅ Vídeo final criado com sucesso!")
            print(f"📊 Tamanho: {size_mb:.1f} MB")
            print(f"📁 Caminho: {output_file}")
            
            # Obter duração com ffprobe
            try:
                probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 
                           'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                           str(output_file)]
                probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
                duration = float(probe_result.stdout.strip())
                print(f"⏱️  Duração: {duration:.1f} segundos ({duration/60:.1f} min)")
                
                if duration > 180:
                    print(f"⚠️  ATENÇÃO: Vídeo tem {duration:.0f}s - precisa ser cortado para 3min!")
            except:
                pass
        else:
            print(f"❌ Erro ffmpeg:")
            print(result.stderr[-500:])  # Últimos 500 chars do erro
            
    except FileNotFoundError:
        print("❌ ffmpeg não encontrado. Instale com: sudo apt install ffmpeg")

if __name__ == '__main__':
    join_videos()
