"""
Sonolus FastAPI CLI
"""
import argparse
import sys
from pathlib import Path

def create_project():
    """新しいSonolus FastAPIプロジェクトを作成"""
    parser = argparse.ArgumentParser(description='Create a new Sonolus FastAPI project')
    parser.add_argument('name', help='Project name')
    args = parser.parse_args(sys.argv[2:])
    
    project_name = args.name
    project_path = Path(project_name)
    
    if project_path.exists():
        print(f"Error: Directory '{project_name}' already exists.")
        sys.exit(1)
    
    # プロジェクト構造を作成
    project_path.mkdir()
    (project_path / 'main.py').write_text('''from sonolus_fastapi import Sonolus
from sonolus_fastapi.backend import StorageBackend
from sonolus_fastapi.pack import freepackpath

sonolus = Sonolus(
    address='https://example.com', # サーバーアドレスを指定してください Specify your server address
    port=8000, # サーバーポートを指定してください Specify your server port
    enable_cors=True, # CORSを有効にするかどうか Whether to enable CORS
    dev=True, # 開発モード Development mode
    session_store=MemorySessionStore(), # セッションストアを指定 Specify session store
    backend=StorageBackend.MEMORY, # ストレージバックエンドを指定 Specify storage backend
)

if __name__ == "__main__":
    import uvicorn
    sonolus.load(freepackpath)
    uvicorn.run(sonolus.app, host="0.0.0.0", port=8000)
''')
    
    print(f"✓ Created project '{project_name}'")
    print(f"\nTo get started:")
    print(f"  cd {project_name}")
    print(f"  python main.py")

def show_version():
    """バージョン情報を表示"""
    from . import __version__
    print(f"sonolus-fastapi version {__version__}")

def show_info():
    """プロジェクト情報を表示"""
    from . import __version__, __author__
    print(f"Sonolus FastAPI v{__version__}")
    print(f"Author: {__author__}")
    print(f"\nDocumentation: https://sonolus-fastapi.pim4n-net.com")
    print(f"Repository: https://github.com/Piliman22/sonolus-fastapi/")

def main():
    """メインCLIエントリーポイント"""
    parser = argparse.ArgumentParser(
        description='Sonolus FastAPI CLI',
        usage='''sonolus-fastapi <command> [<args>]

Available commands:
   create      Create a new Sonolus FastAPI project
   version     Show version information
   info        Show project information
''')
    parser.add_argument('command', help='Command to run')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    args = parser.parse_args(sys.argv[1:2])
    
    commands = {
        'create': create_project,
        'version': show_version,
        'info': show_info,
    }
    
    if args.command not in commands:
        print(f"Error: Unknown command '{args.command}'")
        parser.print_help()
        sys.exit(1)
    
    commands[args.command]()


if __name__ == '__main__':
    main()