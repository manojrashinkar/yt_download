import streamlit as st
import yt_dlp
import ffmpeg
import tempfile
import os

st.set_page_config(page_title="YouTube Downloader & MP3 Converter", page_icon="🎧", layout="centered")
st.title("🎬 YouTube Downloader & MP3 Converter (yt-dlp + ffmpeg)")

tabs = st.tabs(["📥 YouTube Video Downloader", "🎵 YouTube → MP3", "⬆️ Upload Video → MP3"])

# ------------------- TAB 1: YouTube Video Downloader -------------------
with tabs[0]:
    st.header("📥 Download YouTube Video")
    url = st.text_input("Enter YouTube video URL", key="video_url")

    if url:
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)

            st.image(info.get('thumbnail'), caption=info.get('title'))
            st.write(f"**Title:** {info.get('title')}")
            st.write(f"**Uploader:** {info.get('uploader')}")
            st.write(f"**Duration:** {info.get('duration')//60} min {info.get('duration')%60} sec")
            st.write(f"**Views:** {info.get('view_count'):,}")

            # List available video heights
            formats = [f for f in info['formats'] if f['vcodec'] != 'none']
            resolutions = sorted(list({f.get('height') for f in formats if f.get('height')}), reverse=True)
            choice = st.selectbox("Select Resolution", resolutions)

            if st.button("Download Video"):
                temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                format_str = f"bestvideo[height<={choice}]+bestaudio/best[height<={choice}]"
                opts = {'format': format_str, 'outtmpl': temp_video, 'merge_output_format': 'mp4'}

                with st.spinner("Downloading and merging video..."):
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        ydl.download([url])

                st.success("✅ Download complete!")
                st.download_button("⬇️ Download Video", open(temp_video, "rb"), file_name=f"{info.get('title')}.mp4")
                os.remove(temp_video)

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ------------------- TAB 2: YouTube → MP3 -------------------
with tabs[1]:
    st.header("🎵 Convert YouTube Video to MP3")
    yt_url = st.text_input("Enter YouTube URL for MP3", key="mp3_url")

    if yt_url:
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(yt_url, download=False)
            st.image(info.get('thumbnail'), caption=info.get('title'))

            if st.button("Convert to MP3"):
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                mp3_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name

                # Download best audio
                opts = {'format':'bestaudio/best', 'outtmpl': temp_file}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([yt_url])

                # Convert to MP3
                ffmpeg.input(temp_file).output(mp3_file, format='mp3', audio_bitrate='192k').run(overwrite_output=True)
                os.remove(temp_file)

                st.success("✅ MP3 conversion complete!")
                st.download_button("⬇️ Download MP3", open(mp3_file, "rb"), file_name=f"{info.get('title')}.mp3")
                os.remove(mp3_file)

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ------------------- TAB 3: Upload Video → MP3 -------------------
with tabs[2]:
    st.header("⬆️ Upload Video and Convert to MP3")
    uploaded_file = st.file_uploader("Upload your video file", type=["mp4", "mkv", "mov", "avi"])

    if uploaded_file:
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_video.write(uploaded_file.read())
        temp_video.close()

        st.video(temp_video.name)

        if st.button("Convert Uploaded Video to MP3"):
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            with st.spinner("Extracting audio..."):
                ffmpeg.input(temp_video.name).output(temp_audio, format='mp3', audio_bitrate='192k').run(overwrite_output=True)

            st.success("✅ Audio extracted successfully!")
            st.download_button("⬇️ Download MP3", open(temp_audio, "rb"), file_name="converted_audio.mp3")

            os.remove(temp_video.name)
            os.remove(temp_audio)
