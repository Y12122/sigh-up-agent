import { CheckCircleFilled, CloudUploadOutlined, ExclamationCircleFilled } from "@ant-design/icons";
import { Button, Progress, Space, Tag, Typography, Upload } from "antd";

export interface UploadRequest {
  file: File;
  materialType: string;
  personRole: string;
}

interface Props {
  onUpload?: (request: UploadRequest) => void;
}

const materials = [
  { label: "董事身份证正面", status: "done", confidence: "识别成功" },
  { label: "董事身份证反面", status: "review", confidence: "待人工确认" },
  { label: "地址证明", status: "missing", materialType: "address_proof" },
  { label: "白纸签名", status: "missing", materialType: "signature" }
];

export function MaterialChecklist({ onUpload = () => undefined }: Props) {
  return (
    <section className="material-section" aria-labelledby="materials-title">
      <div className="section-heading">
        <div>
          <Typography.Title id="materials-title" level={3}>材料上传</Typography.Title>
          <Typography.Text type="secondary">还需补交 2 项</Typography.Text>
        </div>
        <div className="progress-block">
          <Typography.Text strong>6 / 8</Typography.Text>
          <Progress percent={75} showInfo={false} strokeColor="#176b5b" />
        </div>
      </div>
      <div className="material-list">
        {materials.map((item) => (
          <div className="material-row" key={item.label}>
            <Space>
              {item.status === "done" ? <CheckCircleFilled className="status-ok" /> : <ExclamationCircleFilled className={item.status === "missing" ? "status-danger" : "status-warning"} />}
              <div>
                <Typography.Text strong>{item.label}</Typography.Text>
                <div><Typography.Text type="secondary">董事 · {item.status === "missing" ? "未上传" : item.confidence}</Typography.Text></div>
              </div>
            </Space>
            {item.status === "done" && <Tag color="success">已完成</Tag>}
            {item.status === "review" && <Tag color="warning">需复核</Tag>}
            {item.status === "missing" && (
              <Upload
                accept={item.materialType === "address_proof" ? ".pdf,.png,.jpg,.jpeg" : ".png,.jpg,.jpeg"}
                beforeUpload={(file) => {
                  onUpload({ file, materialType: item.materialType!, personRole: "director" });
                  return false;
                }}
                showUploadList={false}
              >
                <Button icon={<CloudUploadOutlined />} aria-label={`上传${item.label}`}>上传</Button>
              </Upload>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

