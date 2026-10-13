import { useEffect, useState, useTransition } from 'react';
import { InboxOutlined } from '@ant-design/icons';
import { Spin, Upload } from 'antd';
import type { UploadProps, UploadFile } from 'antd/es/upload/interface';

const { Dragger } = Upload;

type UploadSuccess = {
	file_path: string;
	lead_sources: { text: string }[];
	validation: {
		found: Record<string, string>;
		missing: string[];
	};
};

export default function PyUpload(p: {
	children?: React.ReactNode;
	onChange?: (path?: string) => void;
	onSuccess?: (data: UploadSuccess) => void;
	onError?: (message: string) => void;
}) {
	const [fileList, setFileList] = useState<UploadFile[]>([]);
	const [isLoading, startTransition] = useTransition();
	const handleUploadClick = async () => {
		startTransition(async () => {
			try {
				const data =
					await window.pywebview?.api?.select_file_and_get_lead_sources();
				if (!data?.file_path) return;
				setFileList([
					{
						uid: '-1',
						name: data.file_path,
						status: 'done',
						url: data.file_path
					}
				]);
				p.onChange?.(data.file_path);
				if (data.lead_sources && data.validation) {
					p.onSuccess?.(data as UploadSuccess);
				}
			} catch (e) {
				const msg = e instanceof Error ? e.message : String(e);
				p.onError?.(msg);
				setFileList([]);
			}
		});
	};
	useEffect(() => {
		window.pywebview?.api?.get_file_path().then(path => {
			if (path) {
				p.onChange?.(path);
				setFileList([{ uid: '-1', name: path, status: 'done', url: path }]);
			}
		});
	}, []);
	const props: UploadProps = {
		listType: 'picture',
		name: 'file',
		openFileDialogOnClick: false,
		style: { width: '100%' },
		disabled: isLoading,
		beforeUpload() {
			return Upload.LIST_IGNORE;
		},
		fileList: fileList,
		showUploadList: {
			showPreviewIcon: false,
			showDownloadIcon: false,
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
		<Spin spinning={isLoading} description="Reading file…">
			<div onClick={handleUploadClick} id="drop-area">
				<Dragger {...props}>
					<p className="ant-upload-drag-icon">
						<InboxOutlined />
					</p>
					<p className="ant-upload-text"> Click this area to upload </p>
				</Dragger>
			</div>
		</Spin>
	);
}

