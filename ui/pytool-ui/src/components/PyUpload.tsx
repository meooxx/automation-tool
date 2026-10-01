import { useEffect, useState } from 'react';
import { InboxOutlined } from '@ant-design/icons';
import { Upload } from 'antd';
import type { UploadProps, UploadFile } from 'antd/es/upload/interface';

const { Dragger } = Upload;

export default function PyUpload(p: {
	children?: React.ReactNode;
	onSuccess?: (filePath: string) => void;
}) {
	const [fileList, setFileList] = useState<UploadFile[]>([]);
	const handleUploadClick = async () => {
		const path = await window.pywebview?.api?.select_file();
		if (path) {
			p.onSuccess?.(path);
			setFileList([{ uid: '-1', name: path, status: 'done', url: path }]);
		}
	};
	useEffect(() => {
		window.pywebview?.api?.get_file_path().then(path => {
			if (path) {
				// p.onSuccess?.(path);
				setFileList([{ uid: '-1', name: path, status: 'done', url: path }]);
			}
		});
	}, []);
	const props: UploadProps = {
		listType: 'picture',
		name: 'file',
		openFileDialogOnClick: false,
		beforeUpload() {
			return Upload.LIST_IGNORE;
		},
		fileList: fileList,
		showUploadList: {
			showPreviewIcon: false,
			showDownloadIcon: false,
			// downloadIcon: 'Download',
			showRemoveIcon: false,
			removeIcon: null,
			previewIcon: null
		},
		onPreview() {
			return false;
		},
		onDrop() {
			return false;
		}
	};
	return (
		<>
			<div onClick={handleUploadClick} id="drop-area">
				<Dragger {...props}>
					<p className="ant-upload-drag-icon">
						<InboxOutlined />
					</p>
					<p className="ant-upload-text"> Click this area to upload </p>
					<p className="ant-upload-hint"> Support for a single.</p>
				</Dragger>
			</div>
		</>
	);
}

