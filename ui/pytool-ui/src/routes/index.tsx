import { createFileRoute } from '@tanstack/react-router';
import { Row, Col, message, Upload, DatePicker, Space } from 'antd';
import { useState } from 'react';
export const Route = createFileRoute('/')({ component: Home });
import { InboxOutlined } from '@ant-design/icons';
import type { UploadProps, UploadFile } from 'antd/es/upload/interface';
const { Dragger } = Upload;
declare global {
	interface Window {
		pywebview?: {
			api?: {
				bind_drop_event: (selector: string) => Promise<boolean>;
				unbind_drop_event: (selector: string) => Promise<boolean>;
				select_file: () => Promise<string | null>;
			};
		};
	}
}

function Home() {
	const [messageApi, contextHolder] = message.useMessage();
	const [fileList, setFileList] = useState<UploadFile[]>([]);
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

	const handleUploadClick = async () => {
		const path = await window.pywebview?.api?.select_file();
		if (path) {
			messageApi.success(`Choosed: ${path}`);
			setFileList([{ uid: '-1', name: path, status: 'done', url: path }]);
		}
	};

	return (
		<>
			<div>
				{contextHolder}
				<Row gutter={8}>
					<Col sm={12} lg={8}>
						<Space vertical style={{ width: '100%' }}>
							<div onClick={handleUploadClick} id="drop-area">
								<Dragger {...props}>
									<p className="ant-upload-drag-icon">
										<InboxOutlined />
									</p>
									<p className="ant-upload-text">Click this area to upload</p>
									<p className="ant-upload-hint">Support for a single.</p>
								</Dragger>
							</div>
							<DatePicker style={{ width: '100%' }} picker="month" />
						</Space>
					</Col>
					<Col sm={12} lg={8}></Col>
					<Col sm={12} lg={8}></Col>
				</Row>
			</div>
		</>
	);
}

